"""Fetches public repo metadata as evidence for the Profiler agent.

Uses the unauthenticated GitHub API (60 requests/hour). Network failures are
swallowed and reported inline so a rate limit or offline demo never breaks
the pipeline; the Profiler just gets less corroborating evidence. The caller
gets the failed URLs back too (not just swallowed silently), so a thin
evidence result can be explained instead of looking arbitrary, see
docs/requirements.md NFR-4.
"""

import re

import httpx

_REPO_URL_RE = re.compile(r"github\.com/([^/]+)/([^/]+?)(?:\.git)?/?$")


def _parse_owner_repo(url: str) -> tuple[str, str] | None:
    match = _REPO_URL_RE.search(url.strip())
    if not match:
        return None
    return match.group(1), match.group(2)


def fetch_repo_summaries(github_urls: list[str]) -> tuple[str, list[str]]:
    if not github_urls:
        return "No GitHub repositories provided.", []

    summaries = []
    failed_urls = []
    for url in github_urls:
        parsed = _parse_owner_repo(url)
        if not parsed:
            summaries.append(f"{url}: could not parse as a GitHub repo URL.")
            failed_urls.append(url)
            continue
        owner, repo = parsed
        try:
            with httpx.Client(timeout=5.0) as client:
                resp = client.get(f"https://api.github.com/repos/{owner}/{repo}")
                resp.raise_for_status()
                data = resp.json()
            languages_resp = client.get(
                f"https://api.github.com/repos/{owner}/{repo}/languages", timeout=5.0
            )
            languages = list(languages_resp.json().keys()) if languages_resp.status_code == 200 else []

            # Fetch README
            readme_text = ""
            readme_resp = client.get(
                f"https://api.github.com/repos/{owner}/{repo}/readme",
                headers={"Accept": "application/vnd.github.v3.raw"},
                timeout=5.0,
            )
            if readme_resp.status_code == 200:
                readme_text = readme_resp.text[:1200].replace("\n", " ").strip()

            # Fetch dependencies if requirements.txt or package.json exists
            deps = []
            for dep_file in ["requirements.txt", "package.json", "pyproject.toml"]:
                dep_resp = client.get(
                    f"https://api.github.com/repos/{owner}/{repo}/contents/{dep_file}",
                    headers={"Accept": "application/vnd.github.v3.raw"},
                    timeout=5.0,
                )
                if dep_resp.status_code == 200:
                    dep_content = dep_resp.text[:800]
                    deps.append(f"{dep_file}: {dep_content.replace('\n', ' ')}")

            summary_item = (
                f"{owner}/{repo}: {data.get('description') or 'no description'}.\n"
                f"  Languages: {', '.join(languages) or 'unknown'}.\n"
                f"  Last pushed: {data.get('pushed_at', 'unknown')}."
            )
            if readme_text:
                summary_item += f"\n  README excerpt: {readme_text}"
            if deps:
                summary_item += f"\n  Dependency files: {' | '.join(deps)}"

            summaries.append(summary_item)
        except (httpx.HTTPError, ValueError) as exc:
            summaries.append(f"{owner}/{repo}: could not fetch ({exc.__class__.__name__}).")
            failed_urls.append(url)

    return "\n".join(summaries), failed_urls

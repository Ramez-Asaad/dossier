from app.tools.github_tool import _parse_owner_repo, fetch_repo_summaries


def test_parse_owner_repo():
    assert _parse_owner_repo("https://github.com/owner/repo") == ("owner", "repo")
    assert _parse_owner_repo("https://github.com/owner/repo.git") == ("owner", "repo")
    assert _parse_owner_repo("invalid_url") is None


def test_fetch_repo_summaries_empty():
    summary, failed = fetch_repo_summaries([])
    assert summary == "No GitHub repositories provided."
    assert failed == []

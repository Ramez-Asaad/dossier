"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { createProfile } from "@/lib/api";

function linesToList(value: string): string[] {
  return value
    .split("\n")
    .map((line) => line.trim())
    .filter(Boolean);
}

export default function HomePage() {
  const router = useRouter();
  const [courses, setCourses] = useState("");
  const [projects, setProjects] = useState("");
  const [githubUrls, setGithubUrls] = useState("");
  const [targetRole, setTargetRole] = useState("");
  const [jobDescription, setJobDescription] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    setError(null);
    setIsSubmitting(true);
    try {
      const { session_id } = await createProfile({
        raw_courses: linesToList(courses),
        raw_projects: linesToList(projects),
        github_urls: linesToList(githubUrls),
        target_role: targetRole.trim() || undefined,
        target_job_description: jobDescription.trim() || undefined,
      });
      router.push(`/generating/${session_id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong generating the plan.");
      setIsSubmitting(false);
    }
  }

  return (
    <main className="texture-grain mx-auto max-w-2xl px-6 py-16">
      <p className="font-mono text-xs uppercase tracking-[0.2em] text-oxblood">Evidence Engine, No. 01</p>

      <h1 className="mt-4 font-display text-4xl font-medium leading-[1.1] sm:text-5xl">
        Stop taking courses.
        <br />
        <em className="text-ink-dim">Start building evidence.</em>
      </h1>

      <p className="mt-5 max-w-lg text-ink-dim">
        Tell it what you&rsquo;ve studied and built. Six agents compare that against what the role actually
        requires, find your highest-value gaps, and hand you one real project to close them.
      </p>

      <hr className="my-10 border-ink-border" />

      <form onSubmit={handleSubmit} className="space-y-7">
        <Field
          label="Courses"
          hint="one per line"
          value={courses}
          onChange={setCourses}
          placeholder={"Neural Networks\nDatabase Management"}
        />
        <Field
          label="Projects"
          hint="one per line, describe what each does"
          value={projects}
          onChange={setProjects}
          placeholder={"Image classifier built with PyTorch, trained on a public dataset"}
        />
        <Field
          label="GitHub repos"
          hint="one per line, optional"
          value={githubUrls}
          onChange={setGithubUrls}
          placeholder={"https://github.com/you/your-project"}
        />
        <div>
          <FieldLabel label="Target role" />
          <input
            className="mt-2 w-full border-b border-ink-border bg-transparent py-2 text-sm outline-none transition-colors focus:border-oxblood"
            value={targetRole}
            onChange={(event) => setTargetRole(event.target.value)}
            placeholder="ML Engineer"
          />
        </div>
        <div>
          <FieldLabel label="Or paste a job description instead" />
          <textarea
            className="mt-2 w-full border-b border-ink-border bg-transparent py-2 text-sm outline-none transition-colors focus:border-oxblood"
            rows={3}
            value={jobDescription}
            onChange={(event) => setJobDescription(event.target.value)}
          />
        </div>

        {error && <p className="text-sm text-oxblood">{error}</p>}

        <button
          type="submit"
          disabled={isSubmitting}
          className="mt-4 bg-ink px-6 py-3 font-display text-base text-paper transition-opacity hover:opacity-90 disabled:opacity-50"
        >
          {isSubmitting ? "Starting..." : "Generate my mission"}
        </button>
      </form>
    </main>
  );
}

function FieldLabel({ label, hint }: { label: string; hint?: string }) {
  return (
    <label className="flex flex-wrap items-baseline gap-2 font-mono text-xs uppercase tracking-wide text-ink-dim">
      {label}
      {hint && <span className="normal-case tracking-normal text-ink-dim/70">({hint})</span>}
    </label>
  );
}

function Field({
  label,
  hint,
  value,
  onChange,
  placeholder,
}: {
  label: string;
  hint?: string;
  value: string;
  onChange: (value: string) => void;
  placeholder: string;
}) {
  return (
    <div>
      <FieldLabel label={label} hint={hint} />
      <textarea
        className="mt-2 w-full border-b border-ink-border bg-transparent py-2 text-sm outline-none transition-colors focus:border-oxblood"
        rows={3}
        value={value}
        onChange={(event) => onChange(event.target.value)}
        placeholder={placeholder}
      />
    </div>
  );
}

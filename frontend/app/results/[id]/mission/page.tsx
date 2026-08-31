"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { getPlan, submitSprint } from "@/lib/api";
import { CheckIcon, LockIcon, WarningIcon } from "@/components/icons";
import type { FinalPlan, SprintResult } from "@/lib/types";

type SprintState = {
  status: "locked" | "unlocked" | "passed";
  submission: string;
  isSubmitting: boolean;
  result: SprintResult | null;
  error: string | null;
};

export default function MissionPage() {
  const params = useParams<{ id: string }>();
  const [plan, setPlan] = useState<FinalPlan | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [sprints, setSprints] = useState<SprintState[]>([]);

  useEffect(() => {
    const cached = sessionStorage.getItem(`plan:${params.id}`);
    const load = cached ? Promise.resolve(JSON.parse(cached) as FinalPlan) : getPlan(params.id);
    load
      .then((loadedPlan) => {
        setPlan(loadedPlan);
        setSprints(
          loadedPlan.mission.requirements.map((_, index) => ({
            status: index === 0 ? "unlocked" : "locked",
            submission: "",
            isSubmitting: false,
            result: null,
            error: null,
          }))
        );
      })
      .catch((err) => setError(err instanceof Error ? err.message : "Could not load this mission."));
  }, [params.id]);

  function updateSprint(index: number, patch: Partial<SprintState>) {
    setSprints((prev) => prev.map((sprint, i) => (i === index ? { ...sprint, ...patch } : sprint)));
  }

  async function handleSubmitSprint(index: number) {
    if (!plan) return;
    const requirement = plan.mission.requirements[index];
    updateSprint(index, { isSubmitting: true, error: null });
    try {
      const result = await submitSprint(params.id, index, [requirement.description], sprints[index].submission);
      const passed = result.results.every((r) => r.status === "pass");
      updateSprint(index, { isSubmitting: false, result, status: passed ? "passed" : "unlocked" });
      if (passed && index + 1 < sprints.length) {
        updateSprint(index + 1, { status: "unlocked" });
      }
    } catch (err) {
      updateSprint(index, { isSubmitting: false, error: err instanceof Error ? err.message : "Evaluation failed." });
    }
  }

  if (error) {
    return (
      <main className="mx-auto max-w-2xl px-6 py-12">
        <p className="text-oxblood">{error}</p>
      </main>
    );
  }

  if (!plan) {
    return (
      <main className="mx-auto max-w-2xl px-6 py-12">
        <p className="text-ink-dim">Loading your mission...</p>
      </main>
    );
  }

  return (
    <main className="texture-grain mx-auto max-w-2xl px-6 py-16">
      <p className="font-mono text-xs uppercase tracking-[0.2em] text-oxblood">Work simulation</p>
      <h1 className="mt-4 font-display text-3xl font-medium">{plan.mission.title}</h1>
      <p className="mt-2 text-ink-dim">{plan.mission.brief}</p>
      <p className="mt-4 text-sm text-ink-dim/80">
        Each sprint below is one requirement from your actual generated mission, tied to one of your real priority
        gaps. Submit what you built, an agent reviews it against that specific requirement, and the next sprint
        unlocks.
      </p>

      <div className="mt-10 divide-y divide-ink-border border-t border-ink-border">
        {plan.mission.requirements.map((requirement, index) => {
          const sprint = sprints[index];
          if (!sprint) return null;
          const isLocked = sprint.status === "locked";
          return (
            <div key={index} className={`py-6 ${isLocked ? "opacity-40" : ""}`}>
              <div className="flex items-center justify-between">
                <h2 className="flex items-center gap-2 font-display text-lg font-medium">
                  <span className="font-mono text-xs text-ink-dim">{String(index + 1).padStart(2, "0")}</span>
                  Sprint {index + 1}
                  {sprint.status === "passed" && (
                    <span className="flex items-center gap-1 font-mono text-xs uppercase tracking-wide text-gold">
                      <CheckIcon className="h-3.5 w-3.5" /> complete
                    </span>
                  )}
                  {isLocked && (
                    <span className="flex items-center gap-1 font-mono text-xs uppercase tracking-wide text-ink-dim">
                      <LockIcon className="h-3.5 w-3.5" /> locked
                    </span>
                  )}
                </h2>
                <span className="font-mono text-xs uppercase tracking-wide text-ink-dim">
                  {requirement.addresses_gap}
                </span>
              </div>
              <p className="mt-2 text-sm text-ink-dim">{requirement.description}</p>

              {!isLocked && sprint.status !== "passed" && (
                <div className="mt-4">
                  <textarea
                    className="w-full border border-ink-border bg-transparent p-3 text-sm outline-none transition-colors focus:border-oxblood"
                    rows={3}
                    placeholder="Describe what you built for this requirement, or paste the relevant code."
                    value={sprint.submission}
                    onChange={(event) => updateSprint(index, { submission: event.target.value })}
                  />
                  <button
                    onClick={() => handleSubmitSprint(index)}
                    disabled={sprint.isSubmitting || !sprint.submission.trim()}
                    className="mt-3 bg-ink px-5 py-2 font-display text-sm text-paper transition-opacity hover:opacity-90 disabled:opacity-40"
                  >
                    {sprint.isSubmitting ? "Reviewing..." : "Submit for review"}
                  </button>
                  {sprint.error && <p className="mt-2 text-sm text-oxblood">{sprint.error}</p>}
                </div>
              )}

              {sprint.result && (
                <ul className="mt-4 space-y-1.5 border-t border-ink-border pt-3">
                  {sprint.result.results.map((r, i) => (
                    <li key={i} className="flex items-start gap-2 text-sm">
                      <span
                        className={`mt-0.5 shrink-0 ${
                          r.status === "pass" ? "text-gold" : r.status === "partial" ? "text-ink-dim" : "text-oxblood"
                        }`}
                      >
                        {r.status === "pass" ? <CheckIcon className="h-4 w-4" /> : <WarningIcon className="h-4 w-4" />}
                      </span>
                      <span className="text-ink-dim">{r.feedback}</span>
                    </li>
                  ))}
                </ul>
              )}
            </div>
          );
        })}
      </div>
    </main>
  );
}

"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { generateBaseline, getPlan } from "@/lib/api";
import { GapTable } from "@/components/GapTable";
import { MissionCard } from "@/components/MissionCard";
import { ReadinessMeter } from "@/components/ReadinessMeter";
import { SkillList } from "@/components/SkillList";
import { WarningIcon } from "@/components/icons";
import type { BaselineResult, FinalPlan } from "@/lib/types";

export default function ResultsPage() {
  const params = useParams<{ id: string }>();
  const [plan, setPlan] = useState<FinalPlan | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [baseline, setBaseline] = useState<BaselineResult | null>(null);
  const [isLoadingBaseline, setIsLoadingBaseline] = useState(false);
  const [baselineError, setBaselineError] = useState<string | null>(null);

  useEffect(() => {
    const cached = sessionStorage.getItem(`plan:${params.id}`);
    if (cached) {
      setPlan(JSON.parse(cached));
      return;
    }
    getPlan(params.id)
      .then(setPlan)
      .catch((err) => setError(err instanceof Error ? err.message : "Could not load this plan."));
  }, [params.id]);

  async function handleCompareToBaseline() {
    setIsLoadingBaseline(true);
    setBaselineError(null);
    try {
      setBaseline(await generateBaseline(params.id));
    } catch (err) {
      setBaselineError(err instanceof Error ? err.message : "Could not generate the baseline comparison.");
    } finally {
      setIsLoadingBaseline(false);
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
        <p className="text-ink-dim">Loading your plan...</p>
      </main>
    );
  }

  return (
    <main className="texture-grain mx-auto max-w-2xl px-6 py-16">
      <p className="font-mono text-xs uppercase tracking-[0.2em] text-oxblood">{plan.target_role}</p>
      <h1 className="mt-4 font-display text-4xl font-medium">Your industry readiness plan</h1>
      <p className="mt-2 text-ink-dim">
        {plan.fully_covered
          ? "Your mission covers every priority gap we found."
          : "Your mission covers most priority gaps. See below for what's left."}
      </p>

      {plan.github_fetch_issues.length > 0 && (
        <div className="mt-6 flex items-start gap-2.5 border border-oxblood/40 bg-oxblood-dim p-4 text-sm text-oxblood">
          <WarningIcon className="mt-0.5 h-4 w-4 shrink-0" />
          <span>
            Could not fetch evidence from {plan.github_fetch_issues.length === 1 ? "this repo" : "these repos"}:{" "}
            {plan.github_fetch_issues.join(", ")}. Skills and gaps below only reflect your courses and project
            descriptions, so this readiness estimate may be lower than it should be.
          </span>
        </div>
      )}

      <div className="mt-10">
        <ReadinessMeter percent={plan.readiness_percent} />
      </div>

      <section className="mt-10">
        <SectionHeading number="01" title="You already demonstrate" />
        <SkillList skills={plan.demonstrated_skills} />
      </section>

      <section className="mt-10">
        <SectionHeading number="02" title="Your highest-value gaps" />
        <GapTable gaps={plan.priority_gaps} targetRole={plan.target_role} />
      </section>

      <section className="mt-10">
        <SectionHeading number="03" title="Your recommended mission" />
        <MissionCard mission={plan.mission} coverage={plan.coverage} />
        <Link
          href={`/results/${params.id}/mission`}
          className="underline-draw mt-4 inline-block font-display text-base text-oxblood"
        >
          Start your mission &rarr;
        </Link>
        <p className="mt-2 text-xs text-ink-dim">
          Work through this mission sprint by sprint. Submit what you build, an agent reviews it against your actual
          requirements above, evidence, not just a plan.
        </p>
      </section>

      <section className="mt-12 border-t border-ink-border pt-8">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <SectionHeading number="04" title="How does this compare to a single AI prompt?" />
          {!baseline && (
            <button
              onClick={handleCompareToBaseline}
              disabled={isLoadingBaseline}
              className="underline-draw font-mono text-xs uppercase tracking-wide text-oxblood disabled:opacity-50"
            >
              {isLoadingBaseline ? "Generating..." : "Compare to baseline"}
            </button>
          )}
        </div>

        {baselineError && <p className="mt-3 text-sm text-oxblood">{baselineError}</p>}

        {baseline && (
          <div className="mt-4 border border-ink-border p-6">
            <p className="text-sm text-ink-dim">
              A single unstructured prompt given the same input, no pipeline, no evidence check, no coverage
              validation.
            </p>
            <h3 className="mt-4 font-display text-lg font-medium">{baseline.recommended_project.title}</h3>
            <p className="mt-1 text-sm text-ink-dim">{baseline.recommended_project.description}</p>
            <p className="mt-4 text-sm">
              <span className="text-ink-dim">Gaps it named: </span>
              {baseline.priority_gaps.join(", ") || "none"}
            </p>
          </div>
        )}
      </section>
    </main>
  );
}

function SectionHeading({ number, title }: { number: string; title: string }) {
  return (
    <h2 className="mb-3 flex items-baseline gap-3 font-display text-xl font-medium">
      <span className="font-mono text-xs text-ink-dim">{number}</span>
      {title}
    </h2>
  );
}

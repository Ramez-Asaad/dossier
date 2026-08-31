"use client";

import { useEffect, useRef, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { streamGeneratePlan } from "@/lib/api";
import { AgentTrace } from "@/components/AgentTrace";
import type { AgentUpdateEvent, FinalPlan } from "@/lib/types";

export default function GeneratingPage() {
  const params = useParams<{ id: string }>();
  const router = useRouter();
  const [events, setEvents] = useState<AgentUpdateEvent[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [plan, setPlan] = useState<FinalPlan | null>(null);
  const started = useRef(false);

  useEffect(() => {
    if (started.current) return;
    started.current = true;

    streamGeneratePlan(params.id, (event) => {
      if (event.type === "agent_update") {
        setEvents((prev) => [...prev, event]);
      }
    })
      .then((finishedPlan) => {
        sessionStorage.setItem(`plan:${params.id}`, JSON.stringify(finishedPlan));
        setPlan(finishedPlan);
      })
      .catch((err) => setError(err instanceof Error ? err.message : "Something went wrong generating your plan."));
  }, [params.id]);

  return (
    <main className="texture-grain mx-auto max-w-2xl px-6 py-16">
      <p className="font-mono text-xs uppercase tracking-[0.2em] text-gold">Building your plan</p>
      <h1 className="mt-4 font-display text-3xl font-medium">Six agents, one real result</h1>
      <p className="mt-2 max-w-md text-ink-dim">
        Watch what each one finds: what you know, what the market wants, where the gaps are, and what to build to
        close them.
      </p>

      <div className="mt-10">
        <AgentTrace events={events} isRunning={!error && !plan} />
      </div>

      {error && (
        <div className="mt-6 border border-oxblood/40 bg-oxblood-dim p-4 text-sm text-oxblood">
          <p className="font-medium">Something broke mid-pipeline.</p>
          <p className="mt-1">{error}</p>
        </div>
      )}

      <div className="mt-10 border-t border-ink-border pt-8">
        <button
          disabled={!plan}
          onClick={() => plan && router.push(`/results/${params.id}`)}
          className="bg-ink px-6 py-3 font-display text-base text-paper transition-opacity hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-30"
        >
          {plan ? "View your results" : "Working..."}
        </button>
      </div>
    </main>
  );
}

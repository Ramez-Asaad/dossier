"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { getTrace } from "@/lib/api";
import { AGENT_ICONS } from "@/components/icons";
import { STEP_META } from "@/components/agentMeta";
import type { AgentUpdateEvent } from "@/lib/types";

export default function TracePage() {
  const params = useParams<{ id: string }>();
  const [events, setEvents] = useState<AgentUpdateEvent[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getTrace(params.id)
      .then(setEvents)
      .catch((err) => setError(err instanceof Error ? err.message : "Could not load this trace."));
  }, [params.id]);

  if (error) {
    return (
      <main className="mx-auto max-w-3xl px-6 py-12">
        <p className="text-oxblood">{error}</p>
      </main>
    );
  }

  if (!events) {
    return (
      <main className="mx-auto max-w-3xl px-6 py-12">
        <p className="text-ink-dim">Loading trace...</p>
      </main>
    );
  }

  if (events.length === 0) {
    return (
      <main className="texture-grain mx-auto max-w-3xl px-6 py-16">
        <p className="font-mono text-xs uppercase tracking-[0.2em] text-oxblood">Trace</p>
        <h1 className="mt-4 font-display text-3xl font-medium">No trace recorded</h1>
        <p className="mt-2 text-ink-dim">
          This session's plan wasn't generated through the live streaming endpoint, so there's nothing captured. A
          trace is recorded automatically the next time you generate a plan from the intake form.
        </p>
      </main>
    );
  }

  return (
    <main className="texture-grain mx-auto max-w-3xl px-6 py-16">
      <p className="font-mono text-xs uppercase tracking-[0.2em] text-oxblood">Trace</p>
      <h1 className="mt-4 font-display text-3xl font-medium">Every agent, input to output</h1>
      <p className="mt-2 max-w-lg text-ink-dim">
        The exact state each agent read, what it added, and the full configuration of every LLM call it made,
        provider, model, token budget, and prompts. Deterministic steps make no LLM call at all, that's shown too.
      </p>

      <div className="mt-10 space-y-10">
        {events.map((event, index) => (
          <TraceStep key={index} event={event} />
        ))}
      </div>
    </main>
  );
}

function TraceStep({ event }: { event: AgentUpdateEvent }) {
  const Icon = AGENT_ICONS[event.agent];
  const meta = STEP_META[event.agent];

  return (
    <section className="border border-ink-border p-6">
      <div className="flex flex-wrap items-baseline gap-x-3 gap-y-1">
        <span className="font-mono text-xs text-ink-dim">{meta.number}</span>
        <Icon className="h-4 w-4 text-oxblood" />
        <h2 className="font-display text-xl font-medium">{meta.label}</h2>
        <p className="font-mono text-xs italic text-ink-dim">&ldquo;{meta.question}&rdquo;</p>
        {event.attempt > 1 && (
          <span className="font-mono text-xs uppercase tracking-wide text-rust">revision {event.attempt - 1}</span>
        )}
      </div>
      <p className="mt-1.5 text-sm text-ink-dim">{event.summary}</p>

      <div className="mt-4 border-t border-ink-border pt-4">
        <p className="font-mono text-xs uppercase tracking-wide text-gold">Configuration</p>
        {event.llm_calls.length === 0 ? (
          <p className="mt-1.5 text-sm text-ink-dim">Deterministic, no LLM call for this step.</p>
        ) : (
          <div className="mt-2 space-y-3">
            {event.llm_calls.map((call, i) => (
              <div key={i} className="text-sm">
                <div className="flex flex-wrap gap-x-4 gap-y-1 font-mono text-xs">
                  <span>
                    <span className="text-ink-dim">provider </span>
                    {call.provider}
                  </span>
                  <span>
                    <span className="text-ink-dim">model </span>
                    {call.model}
                  </span>
                  <span>
                    <span className="text-ink-dim">max_tokens </span>
                    {call.max_tokens}
                  </span>
                </div>
                <details className="mt-2">
                  <summary className="cursor-pointer font-mono text-xs uppercase tracking-wide text-ink-dim">
                    System prompt (instructions)
                  </summary>
                  <pre className="mt-2 max-h-64 overflow-auto whitespace-pre-wrap border border-ink-border bg-paper-panel p-3 font-mono text-xs">
                    {call.system_prompt}
                  </pre>
                </details>
                <details className="mt-2">
                  <summary className="cursor-pointer font-mono text-xs uppercase tracking-wide text-ink-dim">
                    User prompt (input given to the model)
                  </summary>
                  <pre className="mt-2 max-h-64 overflow-auto whitespace-pre-wrap border border-ink-border bg-paper-panel p-3 font-mono text-xs">
                    {call.user_prompt}
                  </pre>
                </details>
              </div>
            ))}
          </div>
        )}
      </div>

      <details open className="mt-4 border-t border-ink-border pt-4">
        <summary className="cursor-pointer font-mono text-xs uppercase tracking-wide text-gold">
          Output (what this step added to the plan)
        </summary>
        <pre className="mt-2 max-h-96 overflow-auto whitespace-pre-wrap border border-ink-border bg-paper-panel p-3 font-mono text-xs">
          {JSON.stringify(event.output, null, 2)}
        </pre>
      </details>

      <details className="mt-3">
        <summary className="cursor-pointer font-mono text-xs uppercase tracking-wide text-ink-dim">
          Input (full state this step read)
        </summary>
        <pre className="mt-2 max-h-96 overflow-auto whitespace-pre-wrap border border-ink-border bg-paper-panel p-3 font-mono text-xs">
          {JSON.stringify(event.input, null, 2)}
        </pre>
      </details>
    </section>
  );
}

"use client";

import { AnimatePresence, motion } from "framer-motion";
import { AGENT_ICONS } from "./icons";
import type { AgentName, AgentUpdateEvent } from "@/lib/types";

const STEP_META: Record<AgentName, { number: string; label: string; question: string }> = {
  profiler: { number: "01", label: "Profiler", question: "What do you actually know?" },
  industry_analyst: { number: "02", label: "Industry Analyst", question: "What does the market require?" },
  skill_mapper: { number: "03", label: "Skill Mapper", question: "How do these connect?" },
  gap_analyst: { number: "04", label: "Gap Analyst", question: "What's missing?" },
  project_architect: { number: "05", label: "Project Architect", question: "What should you build?" },
  validator: { number: "06", label: "Validator", question: "Does this close the gaps?" },
  finalize: { number: "07", label: "Finalize", question: "Assembling your plan" },
};

export function AgentTrace({ events, isRunning }: { events: AgentUpdateEvent[]; isRunning: boolean }) {
  return (
    <div className="divide-y divide-ink-border border-t border-ink-border">
      <AnimatePresence initial={false}>
        {events.map((event, index) => {
          const Icon = AGENT_ICONS[event.agent];
          const meta = STEP_META[event.agent];
          return (
            <motion.div
              key={`${event.agent}-${event.attempt}-${index}`}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.3 }}
              className="flex gap-4 py-4"
            >
              <span className="w-7 shrink-0 pt-0.5 font-mono text-xs text-ink-dim">{meta.number}</span>
              <Icon className="mt-0.5 h-4 w-4 shrink-0 text-oxblood" />
              <div className="min-w-0 flex-1">
                <div className="flex flex-wrap items-baseline gap-x-2 gap-y-1">
                  <p className="font-display text-lg font-medium">{meta.label}</p>
                  <p className="font-mono text-xs italic text-ink-dim">&ldquo;{meta.question}&rdquo;</p>
                  {event.attempt > 1 && (
                    <span className="font-mono text-xs uppercase tracking-wide text-gold">
                      revision {event.attempt - 1}
                    </span>
                  )}
                </div>
                <p className="mt-1 text-sm text-ink-dim">{event.summary}</p>
              </div>
            </motion.div>
          );
        })}
      </AnimatePresence>

      {isRunning && (
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="flex items-center gap-4 py-4">
          <span className="w-7 shrink-0 font-mono text-xs text-ink-dim">
            {String(events.length + 1).padStart(2, "0")}
          </span>
          <motion.span
            className="h-1.5 w-1.5 rounded-full bg-oxblood"
            animate={{ opacity: [0.25, 1, 0.25] }}
            transition={{ duration: 1.3, repeat: Infinity, ease: "easeInOut" }}
          />
          <p className="font-mono text-xs uppercase tracking-wide text-ink-dim">Working...</p>
        </motion.div>
      )}
    </div>
  );
}

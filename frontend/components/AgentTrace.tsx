"use client";

import { AnimatePresence, motion } from "framer-motion";
import { AGENT_ICONS } from "./icons";
import { STEP_META } from "./agentMeta";
import type { AgentUpdateEvent } from "@/lib/types";

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
              <motion.span initial={{ scale: 0.4, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} transition={{ delay: 0.1, type: "spring", stiffness: 300, damping: 15 }}>
                <Icon className="mt-0.5 h-4 w-4 shrink-0 text-gold" />
              </motion.span>
              <div className="min-w-0 flex-1">
                <div className="flex flex-wrap items-baseline gap-x-2 gap-y-1">
                  <p className="font-display text-lg font-medium">{meta.label}</p>
                  <p className="font-mono text-xs italic text-ink-dim">&ldquo;{meta.question}&rdquo;</p>
                  {event.attempt > 1 && (
                    <span className="font-mono text-xs uppercase tracking-wide text-rust">
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
            className="h-1.5 w-1.5 rounded-full bg-gold"
            animate={{ opacity: [0.25, 1, 0.25] }}
            transition={{ duration: 1.3, repeat: Infinity, ease: "easeInOut" }}
          />
          <p className="font-mono text-xs uppercase tracking-wide text-ink-dim">Working...</p>
        </motion.div>
      )}
    </div>
  );
}

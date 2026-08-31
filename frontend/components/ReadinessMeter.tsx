"use client";

import { motion } from "framer-motion";

export function ReadinessMeter({ percent }: { percent: number }) {
  const radius = 46;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference * (1 - percent / 100);

  return (
    <div className="flex items-center gap-6 border-y border-ink-border py-6">
      <div className="relative h-24 w-24 shrink-0">
        <svg viewBox="0 0 100 100" className="h-full w-full -rotate-90">
          <circle cx="50" cy="50" r={radius} className="stroke-ink-border" strokeWidth="1.5" fill="none" />
          <motion.circle
            cx="50"
            cy="50"
            r={radius}
            className="stroke-oxblood"
            strokeWidth="1.5"
            fill="none"
            strokeDasharray={circumference}
            initial={{ strokeDashoffset: circumference }}
            animate={{ strokeDashoffset: offset }}
            transition={{ duration: 1.1, ease: [0.65, 0, 0.35, 1] }}
          />
        </svg>
        <div className="absolute inset-0 flex items-center justify-center">
          <span className="font-display text-2xl font-medium">{percent}%</span>
        </div>
      </div>
      <div>
        <p className="font-mono text-xs uppercase tracking-[0.15em] text-ink-dim">Current readiness</p>
        <p className="mt-1.5 max-w-xs text-sm text-ink-dim">
          Share of your priority gaps this mission is built to close.
        </p>
      </div>
    </div>
  );
}

"use client";

import { useEffect, useState } from "react";
import { motion } from "framer-motion";

const DURATION_MS = 1100;

function useCountUp(target: number, durationMs: number) {
  const [value, setValue] = useState(0);

  useEffect(() => {
    let frame: number;
    const start = performance.now();
    const ease = (t: number) => 1 - Math.pow(1 - t, 3);

    function tick(now: number) {
      const elapsed = Math.min((now - start) / durationMs, 1);
      setValue(Math.round(ease(elapsed) * target));
      if (elapsed < 1) frame = requestAnimationFrame(tick);
    }

    frame = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(frame);
  }, [target, durationMs]);

  return value;
}

export function ReadinessMeter({ percent }: { percent: number }) {
  const radius = 46;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference * (1 - percent / 100);
  const displayed = useCountUp(percent, DURATION_MS);

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
            transition={{ duration: DURATION_MS / 1000, ease: [0.65, 0, 0.35, 1] }}
          />
        </svg>
        <div className="absolute inset-0 flex items-center justify-center">
          <span className="font-display text-2xl font-medium">{displayed}%</span>
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

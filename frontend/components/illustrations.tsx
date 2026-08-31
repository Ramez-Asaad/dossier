"use client";

// Larger decorative line-art illustrations, same stroke language as icons.tsx
// (1.5px stroke, currentColor, rounded caps) but composed as small scenes
// rather than single glyphs. Used for the two moments in the product that
// carry real narrative weight: "here is your dossier" and "this is now
// certified evidence."

import { motion } from "framer-motion";

const draw = {
  hidden: { pathLength: 0, opacity: 0 },
  show: (delay: number) => ({
    pathLength: 1,
    opacity: 1,
    transition: { pathLength: { duration: 1.1, delay, ease: [0.65, 0, 0.35, 1] as const }, opacity: { duration: 0.3, delay } },
  }),
};

export function DossierIllustration({ className }: { className?: string }) {
  return (
    <svg viewBox="0 0 180 130" className={className} fill="none" strokeLinecap="round" strokeLinejoin="round">
      {/* back sheet */}
      <motion.rect
        x="34" y="18" width="92" height="80" rx="1.5"
        stroke="currentColor" strokeWidth="1.3" className="text-ink-border"
        initial="hidden" animate="show" custom={0} variants={draw}
      />
      {/* front folder */}
      <motion.path
        d="M20 40 h100 a4 4 0 0 1 4 4 v56 a4 4 0 0 1 -4 4 H24 a4 4 0 0 1 -4 -4 V44 a4 4 0 0 1 4 -4 z"
        stroke="currentColor" strokeWidth="1.6" className="text-ink"
        initial="hidden" animate="show" custom={0.15} variants={draw}
      />
      <motion.path
        d="M20 40 v-8 a4 4 0 0 1 4 -4 h26 l8 8 h42 a4 4 0 0 1 4 4 v0"
        stroke="currentColor" strokeWidth="1.6" className="text-ink"
        initial="hidden" animate="show" custom={0.35} variants={draw}
      />
      {/* ruled lines suggesting text on the visible sheet */}
      <motion.path d="M40 58 h60" stroke="currentColor" strokeWidth="1.2" className="text-ink-dim"
        initial="hidden" animate="show" custom={0.6} variants={draw} />
      <motion.path d="M40 68 h72" stroke="currentColor" strokeWidth="1.2" className="text-ink-dim"
        initial="hidden" animate="show" custom={0.68} variants={draw} />
      <motion.path d="M40 78 h48" stroke="currentColor" strokeWidth="1.2" className="text-ink-dim"
        initial="hidden" animate="show" custom={0.76} variants={draw} />
      {/* magnifying glass over the evidence */}
      <motion.circle cx="132" cy="86" r="16" stroke="currentColor" strokeWidth="1.8" className="text-oxblood"
        initial="hidden" animate="show" custom={0.9} variants={draw} />
      <motion.path d="M143.5 97.5 L156 110" stroke="currentColor" strokeWidth="2.2" className="text-oxblood"
        initial="hidden" animate="show" custom={1.15} variants={draw} />
    </svg>
  );
}

export function SealIllustration({ className, state }: { className?: string; state: "certified" | "in-progress" }) {
  const color = state === "certified" ? "text-gold" : "text-oxblood";
  const teeth = Array.from({ length: 16 }, (_, i) => (i * 360) / 16);

  return (
    <motion.svg
      viewBox="0 0 100 100"
      className={`${className} ${color}`}
      fill="none"
      initial={{ scale: 1.6, opacity: 0, rotate: -18 }}
      animate={{ scale: 1, opacity: 1, rotate: -6 }}
      transition={{ type: "spring", stiffness: 210, damping: 14, delay: 0.15 }}
    >
      {teeth.map((deg) => (
        <line
          key={deg}
          x1="50"
          y1="6"
          x2="50"
          y2="13"
          stroke="currentColor"
          strokeWidth="2.4"
          strokeLinecap="round"
          transform={`rotate(${deg} 50 50)`}
        />
      ))}
      <circle cx="50" cy="50" r="34" stroke="currentColor" strokeWidth="1.6" />
      <circle cx="50" cy="50" r="27" stroke="currentColor" strokeWidth="1" strokeDasharray="2 3" />
      {state === "certified" ? (
        <path d="M38 51l8 8 16-18" stroke="currentColor" strokeWidth="3.4" strokeLinecap="round" strokeLinejoin="round" />
      ) : (
        <path d="M50 38v14" stroke="currentColor" strokeWidth="3.4" strokeLinecap="round" />
      )}
      {state === "in-progress" && <circle cx="50" cy="60" r="1.8" fill="currentColor" stroke="none" />}
    </motion.svg>
  );
}

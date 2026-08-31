import type { SkillEntry } from "@/lib/types";

const CONFIDENCE_LABEL: Record<SkillEntry["confidence"], string> = {
  low: "low confidence",
  medium: "medium confidence",
  high: "high confidence",
};

const CONFIDENCE_COLOR: Record<SkillEntry["confidence"], string> = {
  low: "text-ink-dim",
  medium: "text-gold",
  high: "text-oxblood",
};

export function SkillList({ skills }: { skills: SkillEntry[] }) {
  if (skills.length === 0) {
    return <p className="text-sm text-ink-dim">No demonstrated skills yet.</p>;
  }

  return (
    <ul className="divide-y divide-ink-border border-y border-ink-border">
      {skills.map((skill) => (
        <li key={skill.name} className="flex items-start justify-between gap-3 py-3">
          <div>
            <p className="font-display font-medium">{skill.name}</p>
            <p className="text-sm text-ink-dim">{skill.evidence}</p>
          </div>
          <span className={`shrink-0 font-mono text-xs uppercase tracking-wide ${CONFIDENCE_COLOR[skill.confidence]}`}>
            {CONFIDENCE_LABEL[skill.confidence]}
          </span>
        </li>
      ))}
    </ul>
  );
}

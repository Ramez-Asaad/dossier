import type { GapEntry } from "@/lib/types";

const PRIORITY_COLOR: Record<GapEntry["priority"], string> = {
  critical: "text-oxblood",
  high: "text-gold",
  medium: "text-ink-dim",
  low: "text-ink-dim",
};

export function GapTable({ gaps, targetRole }: { gaps: GapEntry[]; targetRole: string }) {
  if (gaps.length === 0) {
    return <p className="text-sm text-ink-dim">No priority gaps identified.</p>;
  }

  return (
    <div>
      <table className="w-full text-left text-sm">
        <thead>
          <tr className="border-y border-ink-border font-mono text-xs uppercase tracking-wide text-ink-dim">
            <th className="py-2.5 pr-4 font-normal">Skill</th>
            <th className="py-2.5 pr-4 font-normal">Current</th>
            <th className="py-2.5 pr-4 font-normal">In {targetRole} postings</th>
            <th className="py-2.5 font-normal">Priority</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-ink-border">
          {gaps.map((gap) => (
            <tr key={gap.skill}>
              <td className="py-2.5 pr-4 font-display font-medium">{gap.skill}</td>
              <td className="py-2.5 pr-4 text-ink-dim">{Math.round(gap.current_level * 100)}%</td>
              <td className="py-2.5 pr-4 text-ink-dim">{Math.round(gap.frequency * 100)}%</td>
              <td className={`py-2.5 font-mono text-xs uppercase tracking-wide ${PRIORITY_COLOR[gap.priority]}`}>
                {gap.priority}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      <p className="mt-2 text-xs text-ink-dim/80">
        Postings percentage comes from the curated job postings dataset for this role, not a live market scan.
      </p>
    </div>
  );
}

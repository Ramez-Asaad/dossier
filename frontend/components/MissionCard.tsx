import { CheckIcon, WarningIcon } from "./icons";
import type { CoverageReport, Mission } from "@/lib/types";

export function MissionCard({ mission, coverage }: { mission: Mission; coverage: CoverageReport }) {
  return (
    <div className="border border-ink-border p-6">
      <h3 className="font-display text-xl font-medium">{mission.title}</h3>
      <p className="mt-2 text-sm text-ink-dim">{mission.brief}</p>

      <ul className="mt-5 divide-y divide-ink-border border-y border-ink-border">
        {mission.requirements.map((req) => {
          const isCovered = coverage.covered_gaps.includes(req.addresses_gap);
          return (
            <li key={req.description} className="flex items-start gap-3 py-2.5 text-sm">
              <span className={`mt-0.5 shrink-0 ${isCovered ? "text-gold" : "text-ink-border"}`}>
                <CheckIcon className="h-4 w-4" />
              </span>
              <span>
                {req.description}
                <span className="ml-2 font-mono text-xs uppercase tracking-wide text-ink-dim">
                  {req.addresses_gap}
                </span>
              </span>
            </li>
          );
        })}
      </ul>

      {coverage.uncovered_gaps.length > 0 && (
        <p className="mt-4 flex items-start gap-2 text-sm text-oxblood">
          <WarningIcon className="mt-0.5 h-4 w-4 shrink-0" />
          <span>
            Not yet covered: {coverage.uncovered_gaps.join(", ")}.
            {coverage.recommendation ? ` Recommendation: ${coverage.recommendation}` : ""}
          </span>
        </p>
      )}
    </div>
  );
}

// Hand-drawn line icon set. Deliberately not emoji: consistent 1.5px stroke,
// single accent color via currentColor, 24x24 grid, rounded caps throughout.

type IconProps = { className?: string };

const base = "stroke-current fill-none";
const strokeProps = { strokeWidth: 1.5, strokeLinecap: "round" as const, strokeLinejoin: "round" as const };

export function ProfilerIcon({ className }: IconProps) {
  return (
    <svg viewBox="0 0 24 24" className={`${base} ${className ?? ""}`} {...strokeProps}>
      <circle cx="10.5" cy="10.5" r="6" />
      <path d="M15 15l5.5 5.5" />
      <path d="M8 10.5a2.5 2.5 0 0 1 2.5-2.5" />
    </svg>
  );
}

export function IndustryIcon({ className }: IconProps) {
  return (
    <svg viewBox="0 0 24 24" className={`${base} ${className ?? ""}`} {...strokeProps}>
      <path d="M4 20V10" />
      <path d="M10 20V4" />
      <path d="M16 20v-7" />
      <path d="M20 20v-3" />
      <path d="M3 20h18" />
    </svg>
  );
}

export function SkillMapIcon({ className }: IconProps) {
  return (
    <svg viewBox="0 0 24 24" className={`${base} ${className ?? ""}`} {...strokeProps}>
      <circle cx="5" cy="6" r="2" />
      <circle cx="5" cy="18" r="2" />
      <circle cx="19" cy="12" r="2" />
      <path d="M7 6.5l10 4.7" />
      <path d="M7 17.5l10 -4.7" />
    </svg>
  );
}

export function TargetIcon({ className }: IconProps) {
  return (
    <svg viewBox="0 0 24 24" className={`${base} ${className ?? ""}`} {...strokeProps}>
      <circle cx="12" cy="12" r="8.5" />
      <circle cx="12" cy="12" r="4.5" />
      <circle cx="12" cy="12" r="0.75" fill="currentColor" stroke="none" />
    </svg>
  );
}

export function BlueprintIcon({ className }: IconProps) {
  return (
    <svg viewBox="0 0 24 24" className={`${base} ${className ?? ""}`} {...strokeProps}>
      <rect x="4" y="4" width="16" height="16" rx="1" />
      <path d="M4 9h16" />
      <path d="M9 9v11" />
      <path d="M13.5 12.5h4" />
      <path d="M13.5 15.5h4" />
    </svg>
  );
}

export function ShieldCheckIcon({ className }: IconProps) {
  return (
    <svg viewBox="0 0 24 24" className={`${base} ${className ?? ""}`} {...strokeProps}>
      <path d="M12 3.5l7 3v5.2c0 4.4-2.9 7.7-7 8.8-4.1-1.1-7-4.4-7-8.8V6.5z" />
      <path d="M9 12l2 2 4-4.2" />
    </svg>
  );
}

export function FlagIcon({ className }: IconProps) {
  return (
    <svg viewBox="0 0 24 24" className={`${base} ${className ?? ""}`} {...strokeProps}>
      <path d="M6 3v18" />
      <path d="M6 4.5h11l-2.5 3.5L17 11.5H6" />
    </svg>
  );
}

export function CheckIcon({ className }: IconProps) {
  return (
    <svg viewBox="0 0 24 24" className={`${base} ${className ?? ""}`} {...strokeProps}>
      <path d="M5 12.5l4.5 4.5L19 7" />
    </svg>
  );
}

export function WarningIcon({ className }: IconProps) {
  return (
    <svg viewBox="0 0 24 24" className={`${base} ${className ?? ""}`} {...strokeProps}>
      <path d="M12 4l9 16H3z" />
      <path d="M12 10v4" />
      <circle cx="12" cy="17" r="0.6" fill="currentColor" stroke="none" />
    </svg>
  );
}

export function LockIcon({ className }: IconProps) {
  return (
    <svg viewBox="0 0 24 24" className={`${base} ${className ?? ""}`} {...strokeProps}>
      <rect x="5" y="10.5" width="14" height="9" rx="1.5" />
      <path d="M8 10.5V7a4 4 0 0 1 8 0v3.5" />
    </svg>
  );
}

export function ArrowRightIcon({ className }: IconProps) {
  return (
    <svg viewBox="0 0 24 24" className={`${base} ${className ?? ""}`} {...strokeProps}>
      <path d="M4 12h15" />
      <path d="M13 6l6 6-6 6" />
    </svg>
  );
}

export function SparkIcon({ className }: IconProps) {
  return (
    <svg viewBox="0 0 24 24" className={`${base} ${className ?? ""}`} {...strokeProps}>
      <path d="M12 3v4.5" />
      <path d="M12 16.5V21" />
      <path d="M3 12h4.5" />
      <path d="M16.5 12H21" />
      <path d="M5.6 5.6l3.2 3.2" />
      <path d="M15.2 15.2l3.2 3.2" />
      <path d="M18.4 5.6l-3.2 3.2" />
      <path d="M8.8 15.2l-3.2 3.2" />
    </svg>
  );
}

export const AGENT_ICONS = {
  profiler: ProfilerIcon,
  industry_analyst: IndustryIcon,
  skill_mapper: SkillMapIcon,
  gap_analyst: TargetIcon,
  project_architect: BlueprintIcon,
  validator: ShieldCheckIcon,
  finalize: FlagIcon,
} as const;

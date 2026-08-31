// Mirrors backend/app/state.py. Keep in sync by hand for the hackathon MVP;
// a generated client from the FastAPI OpenAPI schema is a reasonable
// post-MVP upgrade.

export type Confidence = "low" | "medium" | "high";
export type Importance = "low" | "medium" | "high";
export type Priority = "low" | "medium" | "high" | "critical";

export interface SkillEntry {
  name: string;
  evidence: string;
  confidence: Confidence;
}

export interface GapEntry {
  skill: string;
  current_level: number;
  market_importance: Importance;
  priority: Priority;
  frequency: number;
}

export interface MissionRequirement {
  description: string;
  addresses_gap: string;
}

export interface Mission {
  title: string;
  brief: string;
  requirements: MissionRequirement[];
}

export interface CoverageReport {
  covered_gaps: string[];
  uncovered_gaps: string[];
  recommendation: string | null;
}

export interface FinalPlan {
  target_role: string;
  readiness_percent: number;
  demonstrated_skills: SkillEntry[];
  priority_gaps: GapEntry[];
  mission: Mission;
  coverage: CoverageReport;
  revisions_used: number;
  fully_covered: boolean;
  github_fetch_issues: string[];
}

export interface BaselineResult {
  demonstrated_skills: string[];
  priority_gaps: string[];
  recommended_project: {
    title: string;
    description: string;
  };
}

export type AgentName =
  | "profiler"
  | "industry_analyst"
  | "skill_mapper"
  | "gap_analyst"
  | "project_architect"
  | "validator"
  | "finalize";

export interface AgentUpdateEvent {
  type: "agent_update";
  agent: AgentName;
  attempt: number;
  summary: string;
  data: Record<string, unknown>;
}

export interface StreamDoneEvent {
  type: "done";
}

export interface StreamErrorEvent {
  type: "error";
  message: string;
}

export type StreamEvent = AgentUpdateEvent | StreamDoneEvent | StreamErrorEvent;

export interface SprintResult {
  results: { requirement: string; status: "pass" | "fail" | "partial"; feedback: string }[];
  next_sprint_unlocked: boolean;
}

export interface ProfileInput {
  raw_courses: string[];
  raw_projects: string[];
  github_urls: string[];
  target_role?: string;
  target_job_description?: string;
}

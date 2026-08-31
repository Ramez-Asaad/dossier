import type { AgentName } from "@/lib/types";

export const STEP_META: Record<AgentName, { number: string; label: string; question: string }> = {
  profiler: { number: "01", label: "Profiler", question: "What do you actually know?" },
  industry_analyst: { number: "02", label: "Industry Analyst", question: "What does the market require?" },
  skill_mapper: { number: "03", label: "Skill Mapper", question: "How do these connect?" },
  gap_analyst: { number: "04", label: "Gap Analyst", question: "What's missing?" },
  project_architect: { number: "05", label: "Project Architect", question: "What should you build?" },
  validator: { number: "06", label: "Validator", question: "Does this close the gaps?" },
  finalize: { number: "07", label: "Finalize", question: "Assembling your plan" },
};

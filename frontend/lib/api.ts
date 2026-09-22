import type { AgentUpdateEvent, BaselineResult, FinalPlan, ProfileInput, SprintResult, StreamEvent } from "./types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

async function jsonOrThrow(response: Response) {
  if (!response.ok) {
    const body = await response.text();
    throw new Error(`${response.status} ${response.statusText}: ${body}`);
  }
  return response.json();
}

export async function parseFile(file: File): Promise<{ filename: string; text: string }> {
  const formData = new FormData();
  formData.append("file", file);
  const response = await fetch(`${API_BASE_URL}/parse-file`, {
    method: "POST",
    body: formData,
  });
  return jsonOrThrow(response);
}

export async function createProfile(profile: ProfileInput): Promise<{ session_id: string }> {
  const response = await fetch(`${API_BASE_URL}/profile`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(profile),
  });
  return jsonOrThrow(response);
}

export async function generatePlan(sessionId: string): Promise<FinalPlan> {
  const response = await fetch(`${API_BASE_URL}/sessions/${sessionId}/generate-plan`, {
    method: "POST",
  });
  return jsonOrThrow(response);
}

export async function getPlan(sessionId: string): Promise<FinalPlan> {
  const response = await fetch(`${API_BASE_URL}/sessions/${sessionId}/plan`);
  return jsonOrThrow(response);
}

export async function generateBaseline(sessionId: string): Promise<BaselineResult> {
  const response = await fetch(`${API_BASE_URL}/sessions/${sessionId}/generate-baseline`, {
    method: "POST",
  });
  return jsonOrThrow(response);
}

export async function submitSprint(
  sessionId: string,
  sprintIndex: number,
  requirements: string[],
  submissionDescription: string
): Promise<SprintResult> {
  const response = await fetch(`${API_BASE_URL}/sessions/${sessionId}/sprints/${sprintIndex}/submit`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ requirements, submission_description: submissionDescription }),
  });
  return jsonOrThrow(response);
}

/**
 * Consumes the NDJSON agent trace from /generate-plan/stream, calling
 * onEvent for each line as it arrives. Resolves with the final plan once a
 * "finalize" agent_update event carries it, or rejects on a stream error
 * event or a network failure.
 */
export async function streamGeneratePlan(sessionId: string, onEvent: (event: StreamEvent) => void): Promise<FinalPlan> {
  const response = await fetch(`${API_BASE_URL}/sessions/${sessionId}/generate-plan/stream`, {
    method: "POST",
  });
  if (!response.ok || !response.body) {
    throw new Error(`${response.status} ${response.statusText}`);
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";
  let finalPlan: FinalPlan | null = null;

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });

    const lines = buffer.split("\n");
    buffer = lines.pop() ?? "";
    for (const line of lines) {
      if (!line.trim()) continue;
      const event: StreamEvent = JSON.parse(line);
      onEvent(event);
      if (event.type === "error") {
        throw new Error(event.message);
      }
      if (event.type === "agent_update" && event.agent === "finalize") {
        finalPlan = (event.output as { final_plan: FinalPlan }).final_plan;
      }
    }
  }

  if (!finalPlan) {
    throw new Error("Stream ended without producing a plan.");
  }
  return finalPlan;
}

export async function getTrace(sessionId: string): Promise<AgentUpdateEvent[]> {
  const response = await fetch(`${API_BASE_URL}/sessions/${sessionId}/trace`);
  return jsonOrThrow(response);
}

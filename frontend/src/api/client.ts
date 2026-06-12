export type HealthStatus = {
  ok: boolean;
  service: string;
  status: string;
  timestamp: string;
};

export type ProviderHealth = {
  embedding_provider: string;
  ollama: boolean;
  lm_studio: boolean;
  postgres: boolean;
  qdrant: boolean;
};

export type AgentSummary = {
  name: string;
  description: string;
  capabilities: string[];
};

export type TaskRecord = Record<string, unknown>;
export type ApprovalRecord = Record<string, unknown> & {
  approval_id?: string;
  status?: string;
};
export type MemoryRecord = Record<string, unknown> & {
  memory_id?: string;
  memory_type?: string;
  content?: string;
  tags?: string[];
};
export type VoiceState = {
  mode: string;
  wake_phrase: string;
  microphone_enabled: boolean;
  speaking: boolean;
  updated_at: string;
};
export type SystemTelemetry = {
  timestamp: string;
  hostname: string;
  platform: string;
  python_version: string;
  cpu_count: number;
  cpu_percent: number | null;
  memory_total_bytes: number | null;
  memory_available_bytes: number | null;
  memory_percent: number | null;
  disk_total_bytes: number;
  disk_free_bytes: number;
  disk_percent: number;
  process_id: number;
  gpu_name: string | null;
  gpu_utilization_percent: number | null;
  gpu_memory_used_mb: number | null;
  gpu_memory_total_mb: number | null;
};
export type MissionSummary = {
  tasks_total: number;
  approvals_total: number;
  approvals_pending: number;
  memories_total: number;
  voice_events_total: number;
  audit_log_exists: boolean;
  model_metrics_exists: boolean;
};
export type ModelMetricsSummary = {
  executions_total: number;
  success_total: number;
  failure_total: number;
  fallback_total: number;
  average_latency_ms: number;
  providers: Record<string, { executions: number; successes: number }>;
};

async function request<T>(
  path: string,
  options: RequestInit = {},
): Promise<T> {
  const response = await fetch(`/api${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...(options.headers ?? {}),
    },
    ...options,
  });

  if (!response.ok) {
    const detail = await response.text();
    throw new Error(detail || `Request failed: ${response.status}`);
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return response.json() as Promise<T>;
}

export const api = {
  health: () => request<HealthStatus>("/health"),
  providerHealth: () => request<ProviderHealth>("/providers/health"),
  agents: () => request<{ agents: AgentSummary[] }>("/agents"),
  approvals: () => request<{ approvals: ApprovalRecord[] }>("/approvals"),
  tasks: () => request<{ tasks: TaskRecord[] }>("/tasks"),
  memories: () => request<{ memories: MemoryRecord[] }>("/memory"),
  voiceState: () => request<VoiceState>("/voice/state"),
  voiceHistory: () => request<{ events: Record<string, unknown>[] }>("/voice/history"),
  audit: () => request<{ events: Record<string, unknown>[] }>("/audit"),
  systemTelemetry: () => request<SystemTelemetry>("/telemetry/system"),
  missionSummary: () => request<MissionSummary>("/telemetry/summary"),
  modelMetrics: () => request<ModelMetricsSummary>("/telemetry/models"),
  createTask: (description: string) =>
    request<TaskRecord>("/tasks/route", {
      method: "POST",
      body: JSON.stringify({ description }),
    }),
  approve: (approvalId: string, note?: string) =>
    request<ApprovalRecord>(`/approvals/${approvalId}/approve`, {
      method: "POST",
      body: JSON.stringify({ approver_role: "KurtisC", note }),
    }),
  deny: (approvalId: string, note?: string) =>
    request<ApprovalRecord>(`/approvals/${approvalId}/deny`, {
      method: "POST",
      body: JSON.stringify({ approver_role: "KurtisC", note }),
    }),
  createMemory: (payload: { memory_type: string; content: string; tags: string[] }) =>
    request<MemoryRecord>("/memory", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  deleteMemory: (memoryId: string) =>
    request<void>(`/memory/${memoryId}`, { method: "DELETE" }),
  setVoiceMode: (mode: string) =>
    request<VoiceState>("/voice/mode", {
      method: "PATCH",
      body: JSON.stringify({ mode }),
    }),
  setWakePhrase: (wakePhrase: string) =>
    request<VoiceState>("/voice/wake-phrase", {
      method: "PATCH",
      body: JSON.stringify({ wake_phrase: wakePhrase }),
    }),
};

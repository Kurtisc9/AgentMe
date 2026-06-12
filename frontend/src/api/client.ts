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

async function request<T>(path: string): Promise<T> {
  const response = await fetch(`/api${path}`);
  if (!response.ok) {
    throw new Error(`Request failed: ${response.status}`);
  }
  return response.json() as Promise<T>;
}

export const api = {
  health: () => request<HealthStatus>("/health"),
  providerHealth: () => request<ProviderHealth>("/providers/health"),
  agents: () => request<{ agents: AgentSummary[] }>("/agents"),
  approvals: () => request<{ approvals: unknown[] }>("/approvals"),
  tasks: () => request<{ tasks: unknown[] }>("/tasks"),
};

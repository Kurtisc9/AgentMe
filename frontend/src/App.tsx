import { useEffect, useState } from "react";
import { Activity, Bot, Database, Mic2, ShieldCheck, Wifi } from "lucide-react";

import { api, type AgentSummary, type HealthStatus, type ProviderHealth } from "./api/client";

function StatusPill({ label, online }: { label: string; online: boolean }) {
  return (
    <div className={`status-pill ${online ? "online" : "offline"}`}>
      <span className="status-dot" />
      <span>{label}</span>
    </div>
  );
}

export default function App() {
  const [health, setHealth] = useState<HealthStatus | null>(null);
  const [providers, setProviders] = useState<ProviderHealth | null>(null);
  const [agents, setAgents] = useState<AgentSummary[]>([]);
  const [taskCount, setTaskCount] = useState(0);
  const [approvalCount, setApprovalCount] = useState(0);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    Promise.all([
      api.health(),
      api.providerHealth(),
      api.agents(),
      api.tasks(),
      api.approvals(),
    ])
      .then(([healthData, providerData, agentData, taskData, approvalData]) => {
        setHealth(healthData);
        setProviders(providerData);
        setAgents(agentData.agents);
        setTaskCount(taskData.tasks.length);
        setApprovalCount(approvalData.approvals.length);
      })
      .catch((caught: unknown) => {
        setError(caught instanceof Error ? caught.message : "Unable to load Sage status.");
      });
  }, []);

  return (
    <main className="hud-shell">
      <header className="topbar">
        <div>
          <p className="eyebrow">AGENTME OPERATING SYSTEM</p>
          <h1>SAGE MISSION CONTROL</h1>
        </div>
        <div className="system-state">
          <Activity size={18} />
          <span>{health?.status ?? "connecting"}</span>
        </div>
      </header>

      {error && <div className="error-banner">{error}</div>}

      <section className="hero-grid">
        <article className="panel command-core">
          <div className="panel-heading">
            <Bot size={20} />
            <h2>Command Core</h2>
          </div>
          <div className="core-orb" aria-label="Sage command core">
            <div className="orb-inner">SAGE</div>
          </div>
          <p className="muted">Commander, agents, memory, voice, and approvals linked.</p>
        </article>

        <article className="panel metrics-panel">
          <div className="metric-card">
            <ShieldCheck size={20} />
            <div>
              <span>Pending approvals</span>
              <strong>{approvalCount}</strong>
            </div>
          </div>
          <div className="metric-card">
            <Database size={20} />
            <div>
              <span>Tracked tasks</span>
              <strong>{taskCount}</strong>
            </div>
          </div>
          <div className="metric-card">
            <Mic2 size={20} />
            <div>
              <span>Voice mode</span>
              <strong>READY</strong>
            </div>
          </div>
        </article>
      </section>

      <section className="panel providers-panel">
        <div className="panel-heading">
          <Wifi size={20} />
          <h2>Provider Status</h2>
        </div>
        <div className="status-row">
          <StatusPill label="Ollama" online={providers?.ollama ?? false} />
          <StatusPill label="LM Studio" online={providers?.lm_studio ?? false} />
          <StatusPill label="PostgreSQL" online={providers?.postgres ?? false} />
          <StatusPill label="Qdrant" online={providers?.qdrant ?? false} />
        </div>
      </section>

      <section className="panel agents-panel">
        <div className="panel-heading">
          <Bot size={20} />
          <h2>Specialist Agents</h2>
        </div>
        <div className="agent-grid">
          {agents.map((agent) => (
            <article className="agent-card" key={agent.name}>
              <div className="agent-icon">{agent.name.slice(0, 2).toUpperCase()}</div>
              <h3>{agent.name}</h3>
              <p>{agent.description}</p>
              <div className="tag-row">
                {agent.capabilities.slice(0, 3).map((capability) => (
                  <span key={capability}>{capability}</span>
                ))}
              </div>
            </article>
          ))}
        </div>
      </section>
    </main>
  );
}

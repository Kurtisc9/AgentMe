import { useEffect, useState } from "react";
import {
  Activity,
  Bot,
  Brain,
  ClipboardList,
  Database,
  FileText,
  Mic2,
  Settings,
  ShieldCheck,
  Wifi,
} from "lucide-react";

import { api, type AgentSummary, type HealthStatus, type ProviderHealth } from "./api/client";
import { Sidebar, type HudPage } from "./components/Sidebar";
import { PlaceholderPage } from "./pages/PlaceholderPage";

function StatusPill({ label, online }: { label: string; online: boolean }) {
  return (
    <div className={`status-pill ${online ? "online" : "offline"}`}>
      <span className="status-dot" />
      <span>{label}</span>
    </div>
  );
}

function DataList({ items, emptyText }: { items: unknown[]; emptyText: string }) {
  if (items.length === 0) {
    return <div className="empty-state">{emptyText}</div>;
  }

  return (
    <div className="data-list">
      {items.slice(0, 20).map((item, index) => (
        <pre key={index}>{JSON.stringify(item, null, 2)}</pre>
      ))}
    </div>
  );
}

export default function App() {
  const [activePage, setActivePage] = useState<HudPage>("dashboard");
  const [health, setHealth] = useState<HealthStatus | null>(null);
  const [providers, setProviders] = useState<ProviderHealth | null>(null);
  const [agents, setAgents] = useState<AgentSummary[]>([]);
  const [tasks, setTasks] = useState<unknown[]>([]);
  const [approvals, setApprovals] = useState<unknown[]>([]);
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
        setTasks(taskData.tasks);
        setApprovals(approvalData.approvals);
      })
      .catch((caught: unknown) => {
        setError(caught instanceof Error ? caught.message : "Unable to load Sage status.");
      });
  }, []);

  const renderPage = () => {
    if (activePage === "dashboard") {
      return (
        <>
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
                  <strong>{approvals.length}</strong>
                </div>
              </div>
              <div className="metric-card">
                <Database size={20} />
                <div>
                  <span>Tracked tasks</span>
                  <strong>{tasks.length}</strong>
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
        </>
      );
    }

    if (activePage === "inbox") {
      return (
        <PlaceholderPage title="Inbox" description="Routed tasks and blocked requests." icon={<ClipboardList size={20} />}>
          <DataList items={tasks} emptyText="No routed tasks yet." />
        </PlaceholderPage>
      );
    }

    if (activePage === "approvals") {
      return (
        <PlaceholderPage title="Approvals" description="MEDIUM-risk actions waiting for KurtisC." icon={<ShieldCheck size={20} />}>
          <DataList items={approvals} emptyText="No pending approvals." />
        </PlaceholderPage>
      );
    }

    if (activePage === "agents") {
      return (
        <PlaceholderPage title="Agents" description="Specialist agent roster and capabilities." icon={<Bot size={20} />}>
          <div className="agent-grid">
            {agents.map((agent) => (
              <article className="agent-card" key={agent.name}>
                <div className="agent-icon">{agent.name.slice(0, 2).toUpperCase()}</div>
                <h3>{agent.name}</h3>
                <p>{agent.description}</p>
                <div className="tag-row">
                  {agent.capabilities.map((capability) => (
                    <span key={capability}>{capability}</span>
                  ))}
                </div>
              </article>
            ))}
          </div>
        </PlaceholderPage>
      );
    }

    const pageMap: Record<Exclude<HudPage, "dashboard" | "inbox" | "approvals" | "agents">, JSX.Element> = {
      memory: <PlaceholderPage title="Memory" description="Structured and semantic memory controls." icon={<Brain size={20} />} />,
      voice: <PlaceholderPage title="Voice" description="Voice state, wake phrase, history, and controls." icon={<Mic2 size={20} />} />,
      logs: <PlaceholderPage title="Logs" description="Audit, model, and execution logs." icon={<FileText size={20} />} />,
      settings: <PlaceholderPage title="Settings" description="Provider, model, voice, and safety configuration." icon={<Settings size={20} />} />,
    };

    return pageMap[activePage];
  };

  return (
    <div className="app-layout">
      <Sidebar activePage={activePage} onNavigate={setActivePage} />

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
        {renderPage()}
      </main>
    </div>
  );
}

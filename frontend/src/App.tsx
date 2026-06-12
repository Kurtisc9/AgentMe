import { FormEvent, useEffect, useState } from "react";
import {
  Activity,
  Bot,
  Brain,
  ClipboardList,
  Cpu,
  Database,
  FileText,
  Gauge,
  MemoryStick,
  Mic2,
  Settings,
  ShieldCheck,
  Video,
  Wifi,
} from "lucide-react";

import {
  api,
  type AgentSummary,
  type ApprovalRecord,
  type HealthStatus,
  type MemoryRecord,
  type MissionSummary,
  type ModelMetricsSummary,
  type ProviderHealth,
  type SystemTelemetry,
  type TaskRecord,
  type VoiceState,
} from "./api/client";
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

function MetricCard({
  label,
  value,
  icon,
}: {
  label: string;
  value: string;
  icon: JSX.Element;
}) {
  return (
    <div className="metric-card">
      {icon}
      <div>
        <span>{label}</span>
        <strong>{value}</strong>
      </div>
    </div>
  );
}

export default function App() {
  const [activePage, setActivePage] = useState<HudPage>("dashboard");
  const [health, setHealth] = useState<HealthStatus | null>(null);
  const [providers, setProviders] = useState<ProviderHealth | null>(null);
  const [agents, setAgents] = useState<AgentSummary[]>([]);
  const [tasks, setTasks] = useState<TaskRecord[]>([]);
  const [approvals, setApprovals] = useState<ApprovalRecord[]>([]);
  const [memories, setMemories] = useState<MemoryRecord[]>([]);
  const [voiceState, setVoiceState] = useState<VoiceState | null>(null);
  const [voiceHistory, setVoiceHistory] = useState<Record<string, unknown>[]>([]);
  const [auditEvents, setAuditEvents] = useState<Record<string, unknown>[]>([]);
  const [systemTelemetry, setSystemTelemetry] = useState<SystemTelemetry | null>(null);
  const [missionSummary, setMissionSummary] = useState<MissionSummary | null>(null);
  const [modelMetrics, setModelMetrics] = useState<ModelMetricsSummary | null>(null);
  const [taskInput, setTaskInput] = useState("");
  const [memoryInput, setMemoryInput] = useState("");
  const [memoryType, setMemoryType] = useState("NOTE");
  const [wakePhrase, setWakePhrase] = useState("Sage");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const refresh = async () => {
    const [
      healthData,
      providerData,
      agentData,
      taskData,
      approvalData,
      memoryData,
      currentVoiceState,
      historyData,
      auditData,
      telemetryData,
      summaryData,
      modelMetricData,
    ] = await Promise.all([
      api.health(),
      api.providerHealth(),
      api.agents(),
      api.tasks(),
      api.approvals(),
      api.memories(),
      api.voiceState(),
      api.voiceHistory(),
      api.audit(),
      api.systemTelemetry(),
      api.missionSummary(),
      api.modelMetrics(),
    ]);

    setHealth(healthData);
    setProviders(providerData);
    setAgents(agentData.agents);
    setTasks(taskData.tasks);
    setApprovals(approvalData.approvals);
    setMemories(memoryData.memories);
    setVoiceState(currentVoiceState);
    setWakePhrase(currentVoiceState.wake_phrase);
    setVoiceHistory(historyData.events);
    setAuditEvents(auditData.events);
    setSystemTelemetry(telemetryData);
    setMissionSummary(summaryData);
    setModelMetrics(modelMetricData);
  };

  useEffect(() => {
    void refresh().catch((caught: unknown) => {
      setError(caught instanceof Error ? caught.message : "Unable to load Sage status.");
    });

    const interval = window.setInterval(() => {
      void refresh().catch(() => undefined);
    }, 5000);

    return () => window.clearInterval(interval);
  }, []);

  const runAction = async (action: () => Promise<unknown>) => {
    setBusy(true);
    setError(null);
    try {
      await action();
      await refresh();
    } catch (caught: unknown) {
      setError(caught instanceof Error ? caught.message : "Action failed.");
    } finally {
      setBusy(false);
    }
  };

  const submitTask = (event: FormEvent) => {
    event.preventDefault();
    const description = taskInput.trim();
    if (!description) return;
    void runAction(async () => {
      await api.createTask(description);
      setTaskInput("");
    });
  };

  const submitMemory = (event: FormEvent) => {
    event.preventDefault();
    const content = memoryInput.trim();
    if (!content) return;
    void runAction(async () => {
      await api.createMemory({ memory_type: memoryType, content, tags: [] });
      setMemoryInput("");
    });
  };

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
              <MetricCard label="CPU" value={`${systemTelemetry?.cpu_percent ?? 0}%`} icon={<Cpu size={20} />} />
              <MetricCard label="RAM" value={`${systemTelemetry?.memory_percent ?? 0}%`} icon={<MemoryStick size={20} />} />
              <MetricCard label="GPU" value={`${systemTelemetry?.gpu_utilization_percent ?? 0}%`} icon={<Video size={20} />} />
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

          <section className="telemetry-grid">
            <article className="panel telemetry-card">
              <Gauge size={20} />
              <span>Disk usage</span>
              <strong>{systemTelemetry?.disk_percent ?? 0}%</strong>
            </article>
            <article className="panel telemetry-card">
              <ShieldCheck size={20} />
              <span>Pending approvals</span>
              <strong>{missionSummary?.approvals_pending ?? 0}</strong>
            </article>
            <article className="panel telemetry-card">
              <Database size={20} />
              <span>Memories</span>
              <strong>{missionSummary?.memories_total ?? memories.length}</strong>
            </article>
            <article className="panel telemetry-card">
              <Activity size={20} />
              <span>Model runs</span>
              <strong>{modelMetrics?.executions_total ?? 0}</strong>
            </article>
          </section>
        </>
      );
    }

    if (activePage === "inbox") {
      return (
        <PlaceholderPage title="Inbox" description="Submit and inspect routed tasks." icon={<ClipboardList size={20} />}>
          <form className="control-form" onSubmit={submitTask}>
            <input
              value={taskInput}
              onChange={(event) => setTaskInput(event.target.value)}
              placeholder="Enter a task for Sage"
              disabled={busy}
            />
            <button type="submit" disabled={busy}>Route task</button>
          </form>
          <DataList items={tasks} emptyText="No routed tasks yet." />
        </PlaceholderPage>
      );
    }

    if (activePage === "approvals") {
      return (
        <PlaceholderPage title="Approvals" description="MEDIUM-risk actions waiting for KurtisC." icon={<ShieldCheck size={20} />}>
          {approvals.length === 0 ? (
            <div className="empty-state">No approvals.</div>
          ) : (
            <div className="approval-list">
              {approvals.map((approval, index) => {
                const approvalId = String(approval.approval_id ?? "");
                const pending = approval.status === "PENDING";
                return (
                  <article className="approval-card" key={approvalId || index}>
                    <pre>{JSON.stringify(approval, null, 2)}</pre>
                    {pending && approvalId && (
                      <div className="action-row">
                        <button onClick={() => void runAction(() => api.approve(approvalId))} disabled={busy}>Approve</button>
                        <button className="danger" onClick={() => void runAction(() => api.deny(approvalId))} disabled={busy}>Deny</button>
                      </div>
                    )}
                  </article>
                );
              })}
            </div>
          )}
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

    if (activePage === "memory") {
      return (
        <PlaceholderPage title="Memory" description="Create and remove structured memories." icon={<Brain size={20} />}>
          <form className="control-form" onSubmit={submitMemory}>
            <select value={memoryType} onChange={(event) => setMemoryType(event.target.value)} disabled={busy}>
              <option value="NOTE">Note</option>
              <option value="PREFERENCE">Preference</option>
              <option value="PROJECT">Project</option>
              <option value="DECISION">Decision</option>
            </select>
            <input
              value={memoryInput}
              onChange={(event) => setMemoryInput(event.target.value)}
              placeholder="Store a memory"
              disabled={busy}
            />
            <button type="submit" disabled={busy}>Save memory</button>
          </form>
          <div className="memory-list">
            {memories.length === 0 ? (
              <div className="empty-state">No memories stored.</div>
            ) : (
              memories.map((memory, index) => {
                const memoryId = String(memory.memory_id ?? "");
                return (
                  <article className="memory-card" key={memoryId || index}>
                    <div>
                      <strong>{String(memory.memory_type ?? "MEMORY")}</strong>
                      <p>{String(memory.content ?? "")}</p>
                    </div>
                    {memoryId && (
                      <button className="danger" onClick={() => void runAction(() => api.deleteMemory(memoryId))} disabled={busy}>Delete</button>
                    )}
                  </article>
                );
              })
            )}
          </div>
        </PlaceholderPage>
      );
    }

    if (activePage === "voice") {
      return (
        <PlaceholderPage title="Voice" description="Voice state, wake phrase, and history." icon={<Mic2 size={20} />}>
          <div className="voice-grid">
            <div className="control-card">
              <label>Voice mode</label>
              <select
                value={voiceState?.mode ?? "OFF"}
                onChange={(event) => void runAction(() => api.setVoiceMode(event.target.value))}
                disabled={busy}
              >
                <option value="OFF">Off</option>
                <option value="PUSH_TO_TALK">Push to talk</option>
                <option value="ALWAYS_LISTENING">Always listening</option>
              </select>
            </div>
            <form className="control-card" onSubmit={(event) => {
              event.preventDefault();
              void runAction(() => api.setWakePhrase(wakePhrase));
            }}>
              <label>Wake phrase</label>
              <input value={wakePhrase} onChange={(event) => setWakePhrase(event.target.value)} disabled={busy} />
              <button type="submit" disabled={busy}>Update</button>
            </form>
          </div>
          <DataList items={voiceHistory} emptyText="No voice history yet." />
        </PlaceholderPage>
      );
    }

    if (activePage === "logs") {
      return (
        <PlaceholderPage title="Logs" description="Audit and execution events." icon={<FileText size={20} />}>
          <div className="telemetry-grid compact">
            <article className="panel telemetry-card">
              <Activity size={20} />
              <span>Successes</span>
              <strong>{modelMetrics?.success_total ?? 0}</strong>
            </article>
            <article className="panel telemetry-card">
              <Activity size={20} />
              <span>Failures</span>
              <strong>{modelMetrics?.failure_total ?? 0}</strong>
            </article>
            <article className="panel telemetry-card">
              <Activity size={20} />
              <span>Fallbacks</span>
              <strong>{modelMetrics?.fallback_total ?? 0}</strong>
            </article>
            <article className="panel telemetry-card">
              <Activity size={20} />
              <span>Avg latency</span>
              <strong>{modelMetrics?.average_latency_ms ?? 0} ms</strong>
            </article>
          </div>
          <DataList items={auditEvents} emptyText="No audit events yet." />
        </PlaceholderPage>
      );
    }

    return (
      <PlaceholderPage title="Settings" description="Provider, model, voice, and safety configuration." icon={<Settings size={20} />}>
        <div className="settings-grid">
          <div className="control-card"><strong>Embedding provider</strong><span>{providers?.embedding_provider ?? "unknown"}</span></div>
          <div className="control-card"><strong>Safety owner</strong><span>KurtisC</span></div>
          <div className="control-card"><strong>API status</strong><span>{health?.status ?? "unknown"}</span></div>
          <div className="control-card"><strong>Host</strong><span>{systemTelemetry?.hostname ?? "unknown"}</span></div>
          <div className="control-card"><strong>GPU</strong><span>{systemTelemetry?.gpu_name ?? "not detected"}</span></div>
          <div className="control-card"><strong>Refresh interval</strong><span>5 seconds</span></div>
        </div>
      </PlaceholderPage>
    );
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

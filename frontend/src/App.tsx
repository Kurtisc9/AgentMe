import { useEffect, useState } from "react";
import { Activity, Bot, Brain, ClipboardList, FileText, Mic2, MonitorCog, Settings, ShieldCheck } from "lucide-react";

import {
  api,
  type AgentSummary,
  type ApprovalRecord,
  type DesktopProfile,
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
import { MissionDashboard } from "./pages/MissionDashboard";
import { PlaceholderPage } from "./pages/PlaceholderPage";
import { TradingDashboard } from "./pages/TradingDashboard";

function DataList({ items, emptyText }: { items: unknown[]; emptyText: string }) {
  if (items.length === 0) return <div className="empty-state">{emptyText}</div>;
  return <div className="data-list">{items.slice(0, 12).map((item, index) => <pre key={index}>{JSON.stringify(item, null, 2)}</pre>)}</div>;
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
  const [desktopProfiles, setDesktopProfiles] = useState<DesktopProfile[]>([]);
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
      desktopData,
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
      api.desktopProfiles(),
    ]);

    setHealth(healthData);
    setProviders(providerData);
    setAgents(agentData.agents);
    setTasks(taskData.tasks);
    setApprovals(approvalData.approvals);
    setMemories(memoryData.memories);
    setVoiceState(currentVoiceState);
    setVoiceHistory(historyData.events);
    setAuditEvents(auditData.events);
    setSystemTelemetry(telemetryData);
    setMissionSummary(summaryData);
    setModelMetrics(modelMetricData);
    setDesktopProfiles(desktopData.profiles);
  };

  useEffect(() => {
    void refresh().catch((caught: unknown) => {
      setError(caught instanceof Error ? caught.message : "Unable to load Sage status.");
    });
    const interval = window.setInterval(() => void refresh().catch(() => undefined), 5000);
    return () => window.clearInterval(interval);
  }, []);

  const renderPage = () => {
    if (activePage === "dashboard") {
      return (
        <MissionDashboard
          health={health}
          providers={providers}
          tasks={tasks}
          approvals={approvals}
          memories={memories}
          missionSummary={missionSummary}
          modelMetrics={modelMetrics}
          systemTelemetry={systemTelemetry}
          voiceState={voiceState}
          desktopProfiles={desktopProfiles}
        />
      );
    }

    if (activePage === "trading") return <TradingDashboard />;
    if (activePage === "inbox") return <PlaceholderPage title="Inbox" description="Routed tasks." icon={<ClipboardList size={20} />}><DataList items={tasks} emptyText="No routed tasks yet." /></PlaceholderPage>;
    if (activePage === "approvals") return <PlaceholderPage title="Approvals" description="Review pending approval records." icon={<ShieldCheck size={20} />}><DataList items={approvals} emptyText="No approvals." /></PlaceholderPage>;
    if (activePage === "agents") return <PlaceholderPage title="Agents" description="Specialist agent roster." icon={<Bot size={20} />}><DataList items={agents} emptyText="No agents loaded." /></PlaceholderPage>;
    if (activePage === "memory") return <PlaceholderPage title="Memory" description="Structured memories and recalls." icon={<Brain size={20} />}><DataList items={memories} emptyText="No memories stored." /></PlaceholderPage>;
    if (activePage === "voice") return <PlaceholderPage title="Voice" description="Voice state and history." icon={<Mic2 size={20} />}><DataList items={[voiceState ?? {}, ...voiceHistory]} emptyText="No voice history yet." /></PlaceholderPage>;
    if (activePage === "desktop") return <PlaceholderPage title="Desktop" description="Desktop command profiles." icon={<MonitorCog size={20} />}><DataList items={desktopProfiles} emptyText="No desktop profiles." /></PlaceholderPage>;
    if (activePage === "logs") return <PlaceholderPage title="Logs" description="Audit and execution events." icon={<FileText size={20} />}><DataList items={auditEvents} emptyText="No audit events yet." /></PlaceholderPage>;

    return <PlaceholderPage title="Settings" description="Provider, model, voice, and safety configuration." icon={<Settings size={20} />}><div className="settings-grid"><div className="control-card"><strong>Embedding provider</strong><span>{providers?.embedding_provider ?? "unknown"}</span></div><div className="control-card"><strong>Safety owner</strong><span>KurtisC</span></div><div className="control-card"><strong>API status</strong><span>{health?.status ?? "unknown"}</span></div><div className="control-card"><strong>GPU</strong><span>{systemTelemetry?.gpu_name ?? "not detected"}</span></div></div></PlaceholderPage>;
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
          <div className="system-state"><Activity size={18} /><span>{health?.status ?? "connecting"}</span></div>
        </header>
        {error && <div className="error-banner">{error}</div>}
        {renderPage()}
      </main>
    </div>
  );
}

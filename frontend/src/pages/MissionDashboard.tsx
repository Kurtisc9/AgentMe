import {
  Activity,
  AlertTriangle,
  BarChart3,
  Bot,
  CalendarDays,
  CheckCircle2,
  Cpu,
  Database,
  Gauge,
  HeartPulse,
  LineChart,
  ListChecks,
  MemoryStick,
  ShieldCheck,
  Target,
  TrendingUp,
  Video,
  Wallet,
  Wifi,
} from "lucide-react";

import type {
  ApprovalRecord,
  DesktopProfile,
  HealthStatus,
  MemoryRecord,
  MissionSummary,
  ModelMetricsSummary,
  ProviderHealth,
  SystemTelemetry,
  TaskRecord,
  VoiceState,
} from "../api/client";

function statusLabel(value: boolean | undefined) {
  return value ? "ONLINE" : "OFFLINE";
}

function MiniMetric({ label, value, icon }: { label: string; value: string; icon: JSX.Element }) {
  return (
    <article className="mission-mini-metric">
      {icon}
      <span>{label}</span>
      <strong>{value}</strong>
    </article>
  );
}

function MissionPanel({
  title,
  icon,
  children,
}: {
  title: string;
  icon: JSX.Element;
  children: React.ReactNode;
}) {
  return (
    <section className="mission-panel panel">
      <div className="panel-heading">
        {icon}
        <h2>{title}</h2>
      </div>
      {children}
    </section>
  );
}

export function MissionDashboard({
  health,
  providers,
  tasks,
  approvals,
  memories,
  missionSummary,
  modelMetrics,
  systemTelemetry,
  voiceState,
  desktopProfiles,
}: {
  health: HealthStatus | null;
  providers: ProviderHealth | null;
  tasks: TaskRecord[];
  approvals: ApprovalRecord[];
  memories: MemoryRecord[];
  missionSummary: MissionSummary | null;
  modelMetrics: ModelMetricsSummary | null;
  systemTelemetry: SystemTelemetry | null;
  voiceState: VoiceState | null;
  desktopProfiles: DesktopProfile[];
}) {
  const pendingApprovals = approvals.filter((approval) => approval.status === "PENDING");
  const latestTasks = tasks.slice(0, 4);
  const projectMemories = memories.filter((memory) => memory.memory_type === "PROJECT").slice(0, 4);
  const favoriteProfiles = desktopProfiles.filter((profile) => profile.favorite).slice(0, 6);
  const systemOnline = health?.ok === true;

  const priorities = [
    "Complete Mission Control Alpha before expanding features.",
    "Protect focus: build one working screen at a time.",
    "Keep trading education active, but do not automate trades.",
  ];

  return (
    <div className="mission-dashboard-v1">
      <section className="mission-hero panel">
        <div>
          <p className="eyebrow">MISSION CONTROL V1</p>
          <h2>What matters right now?</h2>
          <p className="mission-hero-text">
            Finish the system that helps KurtisC see priorities, risks, opportunities, and next actions in under 3 seconds.
          </p>
        </div>
        <div className="mission-orb-wrap">
          <div className="mission-orb">SAGE</div>
          <span>{systemOnline ? "ACTIVE" : "CONNECTING"}</span>
        </div>
      </section>

      <section className="mission-metric-grid">
        <MiniMetric label="CPU" value={`${systemTelemetry?.cpu_percent ?? 0}%`} icon={<Cpu size={20} />} />
        <MiniMetric label="RAM" value={`${systemTelemetry?.memory_percent ?? 0}%`} icon={<MemoryStick size={20} />} />
        <MiniMetric label="GPU" value={`${systemTelemetry?.gpu_utilization_percent ?? 0}%`} icon={<Video size={20} />} />
        <MiniMetric label="Approvals" value={`${missionSummary?.approvals_pending ?? pendingApprovals.length}`} icon={<ShieldCheck size={20} />} />
        <MiniMetric label="Memories" value={`${missionSummary?.memories_total ?? memories.length}`} icon={<Database size={20} />} />
        <MiniMetric label="Model Runs" value={`${modelMetrics?.executions_total ?? 0}`} icon={<Activity size={20} />} />
      </section>

      <section className="mission-grid-main">
        <MissionPanel title="Daily Briefing" icon={<CalendarDays size={20} />}>
          <div className="mission-briefing-list">
            <div><strong>Mode</strong><span>{voiceState?.mode ?? "OFF"}</span></div>
            <div><strong>Wake Phrase</strong><span>{voiceState?.wake_phrase ?? "Sage"}</span></div>
            <div><strong>System</strong><span>{health?.status ?? "connecting"}</span></div>
            <div><strong>Refresh</strong><span>Live every 5 seconds</span></div>
          </div>
        </MissionPanel>

        <MissionPanel title="Top Priorities" icon={<Target size={20} />}>
          <div className="priority-stack">
            {priorities.map((priority, index) => (
              <article className="priority-item" key={priority}>
                <span>{index + 1}</span>
                <p>{priority}</p>
              </article>
            ))}
          </div>
        </MissionPanel>

        <MissionPanel title="What Should I Work On Next?" icon={<ListChecks size={20} />}>
          <div className="next-action-card">
            <strong>Build Mission Control V1</strong>
            <p>Finish the default Mission page first. Do not move into Trading, Voice, or Mobile until this page is working cleanly.</p>
          </div>
        </MissionPanel>

        <MissionPanel title="Chief of Staff Alerts" icon={<AlertTriangle size={20} />}>
          <div className="alert-stack">
            <article><span className="alert-dot warning" />Mission Control is the current execution priority.</article>
            <article><span className="alert-dot" />Trading module is locked, but waits behind dashboard completion.</article>
            <article><span className="alert-dot" />Discipline target: finish before expanding.</article>
          </div>
        </MissionPanel>
      </section>

      <section className="mission-grid-secondary">
        <MissionPanel title="Trading Snapshot" icon={<LineChart size={20} />}>
          <div className="trading-snapshot-grid">
            <article><TrendingUp size={18} /><strong>Watchlists</strong><span>BTC / ETH / SPY / QQQ</span></article>
            <article><Wallet size={18} /><strong>Wallets</strong><span>Whale monitoring queued</span></article>
            <article><BarChart3 size={18} /><strong>Coach</strong><span>Risk first. No auto-trades.</span></article>
          </div>
        </MissionPanel>

        <MissionPanel title="Projects" icon={<CheckCircle2 size={20} />}>
          <div className="project-list">
            {projectMemories.length > 0 ? projectMemories.map((memory) => (
              <article key={memory.memory_id ?? memory.content}>
                <strong>{memory.project ?? "Project"}</strong>
                <span>{memory.summary ?? memory.content}</span>
              </article>
            )) : (
              <article><strong>AgentMe</strong><span>Mission Control Alpha in progress.</span></article>
            )}
          </div>
        </MissionPanel>

        <MissionPanel title="System Health" icon={<HeartPulse size={20} />}>
          <div className="provider-grid">
            <span>Ollama: {statusLabel(providers?.ollama)}</span>
            <span>LM Studio: {statusLabel(providers?.lm_studio)}</span>
            <span>PostgreSQL: {statusLabel(providers?.postgres)}</span>
            <span>Qdrant: {statusLabel(providers?.qdrant)}</span>
            <span>Disk: {systemTelemetry?.disk_percent ?? 0}%</span>
            <span>Host: {systemTelemetry?.hostname ?? "unknown"}</span>
          </div>
        </MissionPanel>

        <MissionPanel title="Approvals" icon={<ShieldCheck size={20} />}>
          <div className="approval-summary">
            <strong>{pendingApprovals.length}</strong>
            <span>pending approval{pendingApprovals.length === 1 ? "" : "s"}</span>
            <p>Medium-risk work stays gated. High-risk work remains manual only.</p>
          </div>
        </MissionPanel>

        <MissionPanel title="Automations" icon={<Bot size={20} />}>
          <div className="automation-summary">
            <span>Successes: {modelMetrics?.success_total ?? 0}</span>
            <span>Failures: {modelMetrics?.failure_total ?? 0}</span>
            <span>Fallbacks: {modelMetrics?.fallback_total ?? 0}</span>
            <span>Avg latency: {modelMetrics?.average_latency_ms ?? 0} ms</span>
          </div>
        </MissionPanel>

        <MissionPanel title="Quick Actions" icon={<Gauge size={20} />}>
          <div className="quick-action-list">
            {favoriteProfiles.length > 0 ? favoriteProfiles.map((profile) => (
              <span key={profile.id}>{profile.name}</span>
            )) : (
              <span>No favorite desktop profiles yet.</span>
            )}
          </div>
        </MissionPanel>
      </section>

      <section className="panel mission-activity-panel">
        <div className="panel-heading">
          <Wifi size={20} />
          <h2>Recent Routed Tasks</h2>
        </div>
        <div className="mission-task-strip">
          {latestTasks.length > 0 ? latestTasks.map((task, index) => (
            <pre key={index}>{JSON.stringify(task, null, 2)}</pre>
          )) : (
            <div className="empty-state compact-empty">No routed tasks yet.</div>
          )}
        </div>
      </section>
    </div>
  );
}

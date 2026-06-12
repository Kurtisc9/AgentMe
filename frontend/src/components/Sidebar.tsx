import {
  Bot,
  Brain,
  ClipboardList,
  FileText,
  Gauge,
  MonitorCog,
  Mic2,
  Settings,
  ShieldCheck,
} from "lucide-react";

export type HudPage =
  | "dashboard"
  | "inbox"
  | "approvals"
  | "agents"
  | "memory"
  | "voice"
  | "desktop"
  | "logs"
  | "settings";

const navItems: { id: HudPage; label: string; icon: typeof Gauge }[] = [
  { id: "dashboard", label: "Dashboard", icon: Gauge },
  { id: "inbox", label: "Inbox", icon: ClipboardList },
  { id: "approvals", label: "Approvals", icon: ShieldCheck },
  { id: "agents", label: "Agents", icon: Bot },
  { id: "memory", label: "Memory", icon: Brain },
  { id: "voice", label: "Voice", icon: Mic2 },
  { id: "desktop", label: "Desktop", icon: MonitorCog },
  { id: "logs", label: "Logs", icon: FileText },
  { id: "settings", label: "Settings", icon: Settings },
];

export function Sidebar({
  activePage,
  onNavigate,
}: {
  activePage: HudPage;
  onNavigate: (page: HudPage) => void;
}) {
  return (
    <aside className="sidebar panel">
      <div className="sidebar-brand">
        <div className="agent-icon">SG</div>
        <div>
          <strong>SAGE</strong>
          <span>Mission Control</span>
        </div>
      </div>

      <nav className="sidebar-nav" aria-label="Mission Control navigation">
        {navItems.map(({ id, label, icon: Icon }) => (
          <button
            key={id}
            className={activePage === id ? "active" : ""}
            onClick={() => onNavigate(id)}
            type="button"
          >
            <Icon size={17} />
            <span>{label}</span>
          </button>
        ))}
      </nav>
    </aside>
  );
}

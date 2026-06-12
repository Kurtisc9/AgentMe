import type { ReactNode } from "react";
import {
  AlertTriangle,
  BarChart3,
  BookOpen,
  Brain,
  CandlestickChart,
  LineChart,
  ShieldCheck,
  Target,
  TrendingDown,
  TrendingUp,
  Wallet,
  Waves,
} from "lucide-react";

function TradingPanel({
  title,
  icon,
  children,
}: {
  title: string;
  icon: JSX.Element;
  children: ReactNode;
}) {
  return (
    <section className="trading-panel panel">
      <div className="panel-heading">
        {icon}
        <h2>{title}</h2>
      </div>
      {children}
    </section>
  );
}

const watchlist = [
  { symbol: "BTC", bias: "Watching resistance", alert: "Breakout confirmation needed" },
  { symbol: "ETH", bias: "Trend check", alert: "Watch volume expansion" },
  { symbol: "SPY", bias: "Market direction", alert: "Track support / resistance" },
  { symbol: "QQQ", bias: "Tech momentum", alert: "Watch moving average behavior" },
];

const technicalAlerts = [
  { label: "Uptrend", detail: "Price making higher highs and higher lows", icon: <TrendingUp size={18} /> },
  { label: "Downtrend", detail: "Price making lower highs and lower lows", icon: <TrendingDown size={18} /> },
  { label: "RSI", detail: "Flag overbought / oversold areas", icon: <LineChart size={18} /> },
  { label: "Volume", detail: "Confirm moves before acting", icon: <BarChart3 size={18} /> },
];

const whaleItems = [
  "Large BTC buys above configured threshold",
  "Exchange inflows and outflows",
  "Watched wallet accumulation",
  "Institutional / ETF wallet movement",
];

const journalPrompts = [
  "Why did I enter?",
  "What confirmed the setup?",
  "Where was my invalidation point?",
  "Did I follow my risk rules?",
];

export function TradingDashboard() {
  return (
    <div className="trading-dashboard-alpha">
      <section className="trading-hero panel">
        <div>
          <p className="eyebrow">TRADING OPERATING SYSTEM ALPHA</p>
          <h2>Protect capital. Build skill. Trade with discipline.</h2>
          <p>
            Sage is your market analyst, trading coach, and accountability partner. No automatic trades. No money movement.
          </p>
        </div>
        <div className="trading-rule-card">
          <ShieldCheck size={28} />
          <strong>Rule #1</strong>
          <span>Risk management comes before opportunity.</span>
        </div>
      </section>

      <section className="trading-grid-main">
        <TradingPanel title="Watchlist" icon={<CandlestickChart size={20} />}>
          <div className="watchlist-grid">
            {watchlist.map((item) => (
              <article key={item.symbol}>
                <strong>{item.symbol}</strong>
                <span>{item.bias}</span>
                <small>{item.alert}</small>
              </article>
            ))}
          </div>
        </TradingPanel>

        <TradingPanel title="Technical Alerts" icon={<AlertTriangle size={20} />}>
          <div className="technical-alert-grid">
            {technicalAlerts.map((alert) => (
              <article key={alert.label}>
                {alert.icon}
                <div>
                  <strong>{alert.label}</strong>
                  <span>{alert.detail}</span>
                </div>
              </article>
            ))}
          </div>
        </TradingPanel>
      </section>

      <section className="trading-grid-secondary">
        <TradingPanel title="Whale + Wallet Intelligence" icon={<Wallet size={20} />}>
          <div className="whale-list">
            {whaleItems.map((item) => (
              <div key={item}><Waves size={16} /><span>{item}</span></div>
            ))}
          </div>
        </TradingPanel>

        <TradingPanel title="Trading Journal" icon={<BookOpen size={20} />}>
          <div className="journal-prompt-list">
            {journalPrompts.map((prompt) => <span key={prompt}>{prompt}</span>)}
          </div>
        </TradingPanel>

        <TradingPanel title="Coach Mode" icon={<Brain size={20} />}>
          <div className="coach-card">
            <strong>Today’s lesson</strong>
            <p>Heavy buying is a signal, not a trade. Wait for confirmation from trend, volume, structure, and risk/reward.</p>
          </div>
        </TradingPanel>

        <TradingPanel title="Paper Trading" icon={<Target size={20} />}>
          <div className="paper-trade-card">
            <strong>Status: Ready</strong>
            <span>Track setups before risking real money.</span>
            <span>Goal: process discipline, not excitement.</span>
          </div>
        </TradingPanel>
      </section>
    </div>
  );
}

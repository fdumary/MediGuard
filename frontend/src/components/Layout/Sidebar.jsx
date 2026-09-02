// Left navigation rail: branding, module links, and a live WebSocket
// connection indicator so the demo can visibly show "this is real-time".

import { Activity, LayoutDashboard, Pill, ShieldCheck } from "lucide-react";
import { NavLink } from "react-router-dom";
import { cn } from "../../lib/utils";
import { useSocket } from "../../hooks/useMediGuardSocket";

const NAV_ITEMS = [
  { to: "/", label: "Overview", icon: LayoutDashboard, end: true },
  { to: "/sepsisguard", label: "SepsisGuard", icon: Activity },
  { to: "/crosscare", label: "CrossCare", icon: Pill },
];

export default function Sidebar() {
  const { status } = useSocket();

  return (
    <aside className="fixed inset-y-0 left-0 z-30 flex w-64 flex-col border-r border-base-800 bg-base-900/80 backdrop-blur-xl">
      <div className="flex items-center gap-2.5 px-5 py-6">
        <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-br from-brand-400 to-accent-500 text-base-950 shadow-glow">
          <ShieldCheck className="h-5 w-5" strokeWidth={2.5} />
        </div>
        <div>
          <p className="text-sm font-bold tracking-tight text-base-50">MediGuard</p>
          <p className="text-[11px] text-base-500">Patient Safety Platform</p>
        </div>
      </div>

      <nav className="flex-1 space-y-1 px-3">
        {NAV_ITEMS.map(({ to, label, icon: Icon, end }) => (
          <NavLink
            key={to}
            to={to}
            end={end}
            className={({ isActive }) =>
              cn(
                "flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition-colors",
                isActive
                  ? "bg-brand-500/10 text-brand-400 border border-brand-500/20"
                  : "text-base-400 hover:bg-base-800/60 hover:text-base-100 border border-transparent"
              )
            }
          >
            <Icon className="h-4 w-4" />
            {label}
          </NavLink>
        ))}
      </nav>

      <div className="border-t border-base-800 px-5 py-4">
        <div className="flex items-center gap-2 text-xs">
          <span className="relative flex h-2 w-2">
            {status === "connected" && (
              <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-emerald-400 opacity-75" />
            )}
            <span
              className={cn(
                "relative inline-flex h-2 w-2 rounded-full",
                status === "connected" ? "bg-emerald-400" : status === "connecting" ? "bg-amber-400" : "bg-red-400"
              )}
            />
          </span>
          <span className="text-base-400">
            {status === "connected" ? "Live feed connected" : status === "connecting" ? "Connecting…" : "Feed offline"}
          </span>
        </div>
        <p className="mt-3 text-[11px] leading-relaxed text-base-600">
          API Cloud AI Hackathon 2026
        </p>
      </div>
    </aside>
  );
}

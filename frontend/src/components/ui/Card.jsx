// Base card shell + header used across every panel in the dashboards.

import { cn } from "../../lib/utils";

export default function Card({ className, glow = false, children, ...props }) {
  return (
    <div className={cn(glow ? "card-glow" : "card", "p-5", className)} {...props}>
      {children}
    </div>
  );
}

export function CardHeader({ icon: Icon, title, subtitle, action }) {
  return (
    <div className="mb-4 flex items-start justify-between gap-3">
      <div className="flex items-center gap-3">
        {Icon && (
          <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-base-800 text-brand-400">
            <Icon className="h-4 w-4" />
          </div>
        )}
        <div>
          <h3 className="text-sm font-semibold text-base-50">{title}</h3>
          {subtitle && <p className="text-xs text-base-400">{subtitle}</p>}
        </div>
      </div>
      {action}
    </div>
  );
}

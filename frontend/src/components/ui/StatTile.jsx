// Compact metric tile used in the Overview page and dashboard headers.

import { cn } from "../../lib/utils";

export default function StatTile({ icon: Icon, label, value, tone = "neutral", className }) {
  const toneClass = {
    neutral: "text-base-100",
    brand: "text-brand-400",
    danger: "text-red-400",
    warning: "text-amber-400",
    success: "text-emerald-400",
  }[tone];

  return (
    <div className={cn("card flex items-center gap-3.5 p-4", className)}>
      {Icon && (
        <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-base-800">
          <Icon className={cn("h-5 w-5", toneClass)} />
        </div>
      )}
      <div className="min-w-0">
        <p className="truncate text-xs font-medium uppercase tracking-wide text-base-400">{label}</p>
        <p className={cn("text-xl font-bold tabular-nums", toneClass)}>{value}</p>
      </div>
    </div>
  );
}

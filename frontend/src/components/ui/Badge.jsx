// Small pill used for status/risk/severity labels across the dashboards.

import { cn } from "../../lib/utils";

const TONES = {
  neutral: "bg-base-800 text-base-300 border border-base-700",
  brand: "bg-brand-500/10 text-brand-400 border border-brand-500/30",
  info: "bg-accent-500/10 text-accent-400 border border-accent-500/30",
  success: "bg-emerald-500/10 text-emerald-400 border border-emerald-500/30",
  warning: "bg-amber-500/10 text-amber-400 border border-amber-500/30",
  danger: "bg-red-500/10 text-red-400 border border-red-500/30",
};

export default function Badge({ tone = "neutral", icon: Icon, children, className }) {
  return (
    <span className={cn("badge", TONES[tone] ?? TONES.neutral, className)}>
      {Icon && <Icon className="h-3.5 w-3.5" />}
      {children}
    </span>
  );
}

export function severityTone(severity) {
  switch ((severity || "").toLowerCase()) {
    case "critical":
      return "danger";
    case "severe":
    case "high":
      return "warning";
    case "moderate":
    case "medium":
      return "info";
    default:
      return "success";
  }
}

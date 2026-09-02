// Visualizes an agent pipeline's progress. While a request is in flight it
// sweeps a "running" indicator down the step list (a loading animation, not
// real per-agent telemetry — the backend returns once per full graph run).
// Once a result arrives, each step's checkmark reflects whether that agent
// actually produced output in the response (e.g. SepsisGuard short-circuits
// after Vitals Sentinel when no alert triggers, so later steps show "skipped").

import { Check, Minus, Loader2 } from "lucide-react";
import { useEffect, useState } from "react";
import { cn } from "../lib/utils";

export default function PipelineTracker({ steps, isRunning, result }) {
  const [sweepIndex, setSweepIndex] = useState(0);

  useEffect(() => {
    if (!isRunning) {
      setSweepIndex(0);
      return;
    }
    const interval = setInterval(() => {
      setSweepIndex((i) => Math.min(i + 1, steps.length - 1));
    }, 650);
    return () => clearInterval(interval);
  }, [isRunning, steps.length]);

  return (
    <ol className="space-y-1">
      {steps.map((step, i) => {
        const Icon = step.icon;
        const ran = result ? step.didRun(result) : false;
        const state = !result && isRunning
          ? i <= sweepIndex ? (i === sweepIndex ? "running" : "done") : "pending"
          : result
          ? ran ? "done" : "skipped"
          : "pending";

        return (
          <li
            key={step.name}
            className={cn(
              "flex items-center gap-3 rounded-lg border px-3 py-2.5 transition-colors",
              state === "running" && "border-brand-500/40 bg-brand-500/5",
              state === "done" && "border-emerald-500/20 bg-emerald-500/5",
              state === "skipped" && "border-base-800 bg-base-900/40 opacity-60",
              state === "pending" && "border-base-800 bg-transparent"
            )}
          >
            <StatusIcon state={state} />
            <Icon className="h-4 w-4 shrink-0 text-base-400" />
            <span className="text-sm text-base-200">{step.name}</span>
            <span className="ml-auto text-[11px] uppercase tracking-wide text-base-500">
              {state === "running" ? "Working…" : state === "done" ? "Done" : state === "skipped" ? "Skipped" : ""}
            </span>
          </li>
        );
      })}
    </ol>
  );
}

function StatusIcon({ state }) {
  if (state === "running") return <Loader2 className="h-4 w-4 shrink-0 animate-spin text-brand-400" />;
  if (state === "done") return <Check className="h-4 w-4 shrink-0 text-emerald-400" />;
  if (state === "skipped") return <Minus className="h-4 w-4 shrink-0 text-base-600" />;
  return <span className="h-4 w-4 shrink-0 rounded-full border border-base-700" />;
}

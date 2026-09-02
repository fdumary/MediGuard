// Small inline spinner + a full "empty state" placeholder for panels with no data yet.

import { Loader2 } from "lucide-react";
import { cn } from "../../lib/utils";

export function Spinner({ className }) {
  return <Loader2 className={cn("animate-spin", className)} />;
}

export function EmptyState({ icon: Icon, title, subtitle }) {
  return (
    <div className="flex flex-col items-center justify-center gap-2 py-10 text-center">
      {Icon && <Icon className="h-8 w-8 text-base-600" />}
      <p className="text-sm font-medium text-base-300">{title}</p>
      {subtitle && <p className="max-w-xs text-xs text-base-500">{subtitle}</p>}
    </div>
  );
}

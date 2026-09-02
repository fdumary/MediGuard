// Shared button primitive with primary/secondary/ghost variants and a
// built-in loading spinner state.

import { Loader2 } from "lucide-react";
import { cn } from "../../lib/utils";

const VARIANTS = {
  primary: "btn-primary",
  secondary: "btn-secondary",
  ghost: "btn-ghost",
};

export default function Button({
  variant = "primary",
  loading = false,
  icon: Icon,
  children,
  className,
  disabled,
  ...props
}) {
  return (
    <button
      className={cn(VARIANTS[variant] ?? VARIANTS.primary, className)}
      disabled={disabled || loading}
      {...props}
    >
      {loading ? (
        <Loader2 className="h-4 w-4 animate-spin" />
      ) : (
        Icon && <Icon className="h-4 w-4" />
      )}
      {children}
    </button>
  );
}

import React from "react";
import { clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export type BadgeVariant =
  | "success"
  | "warning"
  | "info"
  | "neutral"
  | "danger"
  | "purple"
  | "amber"
  | "outline";

interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  variant?: BadgeVariant;
  dot?: boolean;
  children: React.ReactNode;
}

export const Badge: React.FC<BadgeProps> = ({
  children,
  variant = "neutral",
  dot = false,
  className,
  ...props
}) => {
  const variantStyles: Record<BadgeVariant, string> = {
    success: "bg-emerald-500/10 text-emerald-400 border-emerald-500/20",
    warning: "bg-amber-500/10 text-amber-400 border-amber-500/20",
    info: "bg-sky-500/10 text-sky-400 border-sky-500/20",
    neutral: "bg-slate-800/80 text-slate-300 border-slate-700/80",
    danger: "bg-red-500/10 text-red-400 border-red-500/20",
    purple: "bg-purple-500/10 text-purple-400 border-purple-500/20",
    amber: "bg-amber-500/15 text-amber-300 border-amber-500/30",
    outline: "bg-transparent text-slate-300 border-slate-700",
  };

  const dotColors: Record<BadgeVariant, string> = {
    success: "bg-emerald-400",
    warning: "bg-amber-400",
    info: "bg-sky-400",
    neutral: "bg-slate-400",
    danger: "bg-red-400",
    purple: "bg-purple-400",
    amber: "bg-amber-400",
    outline: "bg-slate-400",
  };

  return (
    <span
      className={twMerge(
        clsx(
          "inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium border transition-colors",
          variantStyles[variant],
          className
        )
      )}
      {...props}
    >
      {dot && (
        <span
          className={clsx("w-1.5 h-1.5 rounded-full animate-pulse", dotColors[variant])}
        />
      )}
      {children}
    </span>
  );
};

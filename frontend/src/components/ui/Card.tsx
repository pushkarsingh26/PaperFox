import React from "react";
import { clsx } from "clsx";
import { twMerge } from "tailwind-merge";

interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
  hover?: boolean;
  glow?: boolean;
}

export const Card: React.FC<CardProps> = ({
  children,
  hover = false,
  glow = false,
  className,
  ...props
}) => {
  return (
    <div
      className={twMerge(
        clsx(
          "bg-slate-900/70 border border-slate-800/80 rounded-2xl p-6 shadow-xl shadow-black/30 backdrop-blur-xl transition-all duration-200",
          hover && "hover:border-slate-700/80 hover:bg-slate-900/90 hover:shadow-2xl hover:shadow-black/50 hover:-translate-y-0.5",
          glow && "border-amber-500/30 shadow-amber-500/5 glow-card",
          className
        )
      )}
      {...props}
    >
      {children}
    </div>
  );
};

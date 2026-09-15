import React from "react";
import { clsx } from "clsx";
import { twMerge } from "tailwind-merge";

interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
}

export const Card: React.FC<CardProps> = ({ children, className, ...props }) => {
  return (
    <div
      className={twMerge(
        clsx(
          "bg-slate-900/60 border border-slate-800/80 backdrop-blur-xl rounded-xl p-6 shadow-xl shadow-black/20",
          className
        )
      )}
      {...props}
    >
      {children}
    </div>
  );
};

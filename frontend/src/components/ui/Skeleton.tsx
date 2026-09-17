import React from "react";
import { clsx } from "clsx";
import { twMerge } from "tailwind-merge";

interface SkeletonProps extends React.HTMLAttributes<HTMLDivElement> {
  className?: string;
}

export const Skeleton: React.FC<SkeletonProps> = ({ className, ...props }) => {
  return (
    <div
      className={twMerge(
        clsx(
          "animate-pulse rounded-xl bg-slate-800/60 border border-slate-700/20",
          className
        )
      )}
      {...props}
    />
  );
};

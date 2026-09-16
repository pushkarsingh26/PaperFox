import React from "react";
import Image from "next/image";

interface FoxLogoProps {
  className?: string;
  size?: number;
  variant?: "mark" | "full" | "light";
  priority?: boolean;
}

export const FoxLogo: React.FC<FoxLogoProps> = ({
  className = "w-6 h-6",
  size = 32,
  variant = "mark",
  priority = false,
}) => {
  if (variant === "full") {
    return (
      <div className={`flex items-center space-x-2.5 ${className}`}>
        <div className="relative w-8 h-8 shrink-0">
          <Image
            src="/branding/paperfox-fox-mark.svg"
            alt="PaperFox Logo"
            fill
            className="object-contain"
            priority={priority}
          />
        </div>
        <span className="font-extrabold text-xl tracking-tight text-white">
          Paper<span className="text-amber-500">Fox</span>
        </span>
      </div>
    );
  }

  if (variant === "light") {
    return (
      <div className={`flex items-center space-x-2.5 ${className}`}>
        <div className="relative w-8 h-8 shrink-0">
          <Image
            src="/branding/paperfox-fox-mark.svg"
            alt="PaperFox Logo"
            fill
            className="object-contain"
            priority={priority}
          />
        </div>
        <span className="font-extrabold text-xl tracking-tight text-slate-900">
          Paper<span className="text-amber-600">Fox</span>
        </span>
      </div>
    );
  }

  // Standalone Fox mark
  return (
    <div className={`relative shrink-0 flex items-center justify-center ${className}`}>
      <Image
        src="/branding/paperfox-fox-mark.svg"
        alt="PaperFox"
        width={size}
        height={size}
        className="w-full h-full object-contain"
        priority={priority}
      />
    </div>
  );
};

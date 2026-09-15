"use client";

import React, { useState, useEffect } from "react";
import { Card } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Badge } from "@/components/ui/Badge";
import { api } from "@/lib/api";
import { CandidateProfile } from "@/types/profile";
import {
  ArrowUp,
  ArrowDown,
  RotateCcw,
  Save,
  CheckCircle2,
  FileText,
  GraduationCap,
  Briefcase,
  FolderGit2,
  Code2,
  Award,
  Layers,
  Sparkles,
} from "lucide-react";

export const DEFAULT_SECTION_ORDER = [
  "summary",
  "education",
  "experience",
  "projects",
  "skills",
  "certifications",
];

const SECTION_METADATA: Record<
  string,
  { label: string; icon: React.ElementType; description: string }
> = {
  summary: {
    label: "Professional Summary",
    icon: FileText,
    description: "High-level summary of professional background & value",
  },
  education: {
    label: "Education",
    icon: GraduationCap,
    description: "Academic degrees, institutions & graduation dates",
  },
  experience: {
    label: "Work Experience & Internships",
    icon: Briefcase,
    description: "Industry roles, key responsibilities & achievements",
  },
  projects: {
    label: "Key Projects",
    icon: FolderGit2,
    description: "Technical projects with architecture & evidence",
  },
  skills: {
    label: "Technical Skills",
    icon: Code2,
    description: "Grouped skills by language, framework, database & cloud",
  },
  certifications: {
    label: "Certifications",
    icon: Award,
    description: "Verified industry credentials & licenses",
  },
};

interface SectionOrderEditorProps {
  profile: CandidateProfile | null;
  onOrderSaved?: (newOrder: string[]) => void;
  onRegenerateRequested?: () => Promise<void>;
  isGenerating?: boolean;
}

export const SectionOrderEditor: React.FC<SectionOrderEditorProps> = ({
  profile,
  onOrderSaved,
  onRegenerateRequested,
  isGenerating = false,
}) => {
  const [order, setOrder] = useState<string[]>(DEFAULT_SECTION_ORDER);
  const [isSaving, setIsSaving] = useState<boolean>(false);
  const [saveSuccess, setSaveSuccess] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (profile?.section_order && profile.section_order.length > 0) {
      // Ensure all supported sections are present
      const current = [...profile.section_order];
      for (const sec of DEFAULT_SECTION_ORDER) {
        if (!current.includes(sec)) {
          current.push(sec);
        }
      }
      setOrder(current);
    } else {
      setOrder(DEFAULT_SECTION_ORDER);
    }
  }, [profile?.section_order]);

  const moveUp = (index: number) => {
    if (index === 0) return;
    const newOrder = [...order];
    const temp = newOrder[index - 1];
    newOrder[index - 1] = newOrder[index];
    newOrder[index] = temp;
    setOrder(newOrder);
    setSaveSuccess(false);
  };

  const moveDown = (index: number) => {
    if (index === order.length - 1) return;
    const newOrder = [...order];
    const temp = newOrder[index + 1];
    newOrder[index + 1] = newOrder[index];
    newOrder[index] = temp;
    setOrder(newOrder);
    setSaveSuccess(false);
  };

  const resetToDefault = () => {
    setOrder(DEFAULT_SECTION_ORDER);
    setSaveSuccess(false);
  };

  const handleSaveOrder = async () => {
    setIsSaving(true);
    setError(null);
    setSaveSuccess(false);

    try {
      await api.put("/profile", { section_order: order });
      setSaveSuccess(true);
      if (onOrderSaved) {
        onOrderSaved(order);
      }
      setTimeout(() => setSaveSuccess(false), 3000);
    } catch (err: any) {
      const detail = err.response?.data?.detail;
      setError(typeof detail === "string" ? detail : "Failed to save section ordering.");
    } finally {
      setIsSaving(false);
    }
  };

  const handleSaveAndRegenerate = async () => {
    await handleSaveOrder();
    if (onRegenerateRequested) {
      await onRegenerateRequested();
    }
  };

  return (
    <Card className="p-6 space-y-5 border-slate-800 bg-slate-900/60">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-800 pb-3">
        <div className="space-y-0.5">
          <h3 className="text-sm font-bold text-white uppercase tracking-wider flex items-center gap-2">
            <Layers className="w-4 h-4 text-amber-500" /> Resume Section Ordering
          </h3>
          <p className="text-xs text-slate-400">
            Control the exact deterministic sequence of sections in your compiled LaTeX resume.
          </p>
        </div>

        <Button
          type="button"
          variant="ghost"
          size="sm"
          onClick={resetToDefault}
          className="text-xs text-slate-400 hover:text-white"
        >
          <RotateCcw className="w-3.5 h-3.5 mr-1" /> Reset Default
        </Button>
      </div>

      {error && (
        <div className="p-3 bg-red-500/10 border border-red-500/30 rounded-lg text-xs text-red-400">
          {error}
        </div>
      )}

      {saveSuccess && (
        <div className="p-3 bg-emerald-500/10 border border-emerald-500/20 rounded-lg text-xs text-emerald-400 flex items-center gap-2">
          <CheckCircle2 className="w-4 h-4" /> Section ordering preference saved!
        </div>
      )}

      <div className="space-y-2">
        {order.map((secKey, idx) => {
          const meta = SECTION_METADATA[secKey] || {
            label: secKey,
            icon: FileText,
            description: "",
          };
          const Icon = meta.icon;
          const isFirst = idx === 0;
          const isLast = idx === order.length - 1;

          return (
            <div
              key={secKey}
              className="flex items-center justify-between p-3 rounded-lg bg-slate-950/70 border border-slate-800/80 hover:border-slate-700 transition-colors"
            >
              <div className="flex items-center space-x-3">
                <span className="w-5 text-center text-xs font-mono font-bold text-amber-500/80">
                  {idx + 1}
                </span>
                <div className="w-7 h-7 rounded bg-slate-800/60 flex items-center justify-center text-slate-300">
                  <Icon className="w-4 h-4 text-amber-400" />
                </div>
                <div>
                  <p className="text-xs font-semibold text-slate-200">{meta.label}</p>
                  <p className="text-[11px] text-slate-500">{meta.description}</p>
                </div>
              </div>

              <div className="flex items-center space-x-1">
                <Button
                  type="button"
                  variant="ghost"
                  size="sm"
                  onClick={() => moveUp(idx)}
                  disabled={isFirst}
                  className="h-7 w-7 p-0 text-slate-400 hover:text-white disabled:opacity-30"
                  title="Move Up"
                >
                  <ArrowUp className="w-3.5 h-3.5" />
                </Button>
                <Button
                  type="button"
                  variant="ghost"
                  size="sm"
                  onClick={() => moveDown(idx)}
                  disabled={isLast}
                  className="h-7 w-7 p-0 text-slate-400 hover:text-white disabled:opacity-30"
                  title="Move Down"
                >
                  <ArrowDown className="w-3.5 h-3.5" />
                </Button>
              </div>
            </div>
          );
        })}
      </div>

      <div className="pt-2 flex flex-wrap items-center justify-between gap-3">
        <Button
          type="button"
          variant="secondary"
          size="sm"
          onClick={handleSaveOrder}
          isLoading={isSaving}
          className="text-xs font-semibold"
        >
          <Save className="w-3.5 h-3.5 mr-1.5" /> Save Preference
        </Button>

        {onRegenerateRequested && (
          <Button
            type="button"
            variant="primary"
            size="sm"
            onClick={handleSaveAndRegenerate}
            isLoading={isSaving || isGenerating}
            className="text-xs font-semibold"
          >
            <Sparkles className="w-3.5 h-3.5 mr-1.5" /> Save & Recompile PDF
          </Button>
        )}
      </div>
    </Card>
  );
};

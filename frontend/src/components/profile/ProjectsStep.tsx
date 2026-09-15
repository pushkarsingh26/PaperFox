"use client";

import React, { useState } from "react";
import { Project } from "@/types/profile";
import { Input } from "@/components/ui/Input";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { FolderGit2, Plus, Trash2, User, Sparkles, Copy, Check, FileText } from "lucide-react";
import { generateUniversalProjectPrompt } from "@/lib/promptGenerator";

interface ProjectsStepProps {
  projects: Project[];
  onChangeProjects: (items: Project[]) => void;
}

export const ProjectsStep: React.FC<ProjectsStepProps> = ({
  projects,
  onChangeProjects,
}) => {
  const [activePrompts, setActivePrompts] = useState<Record<number, string>>({});
  const [copiedIndex, setCopiedIndex] = useState<number | null>(null);

  const addProject = () => {
    onChangeProjects([
      ...projects,
      {
        name: "",
        description: "",
        description_source: "self",
        technologies: [],
        features: [],
        project_url: "",
        github_url: "",
        repository_url: "",
      },
    ]);
  };

  const updateProject = (index: number, field: keyof Project, value: any) => {
    const updated = [...projects];
    updated[index] = { ...updated[index], [field]: value };
    onChangeProjects(updated);
  };

  const removeProject = (index: number) => {
    onChangeProjects(projects.filter((_, i) => i !== index));
    const newPrompts = { ...activePrompts };
    delete newPrompts[index];
    setActivePrompts(newPrompts);
  };

  const handleGeneratePrompt = (index: number, project: Project) => {
    const promptText = generateUniversalProjectPrompt(project);
    setActivePrompts((prev) => ({ ...prev, [index]: promptText }));
  };

  const handleCopyPrompt = async (index: number, text: string) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopiedIndex(index);
      setTimeout(() => setCopiedIndex(null), 2000);
    } catch (err) {
      console.error("Failed to copy text: ", err);
    }
  };

  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-xl font-bold text-white tracking-tight flex items-center gap-2">
          <FolderGit2 className="w-5 h-5 text-amber-500" /> Projects Repository
        </h2>
        <p className="text-xs text-slate-400 mt-1">
          Add your key technical projects, open source work, or application implementations.
        </p>
      </div>

      {projects.length === 0 ? (
        <Card className="p-8 text-center space-y-4 border-dashed border-slate-800 bg-slate-900/30">
          <FolderGit2 className="w-10 h-10 text-slate-600 mx-auto" />
          <p className="text-sm text-slate-400">No project entries added yet.</p>
          <Button type="button" variant="primary" size="sm" onClick={addProject}>
            <Plus className="w-4 h-4 mr-2" /> Add First Project Entry
          </Button>
        </Card>
      ) : (
        <div className="space-y-6">
          {projects.map((item, idx) => {
            const currentSource = item.description_source || "self";
            const generatedPrompt = activePrompts[idx] || (currentSource === "ai" ? generateUniversalProjectPrompt(item) : "");

            return (
              <Card key={idx} className="p-6 space-y-5 relative border-slate-800 bg-slate-900/80">
                <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                  <span className="text-xs font-semibold text-amber-400 uppercase tracking-wider flex items-center gap-1.5">
                    <FolderGit2 className="w-3.5 h-3.5" /> Project #{idx + 1}
                  </span>
                  <Button
                    type="button"
                    variant="ghost"
                    size="sm"
                    onClick={() => removeProject(idx)}
                    className="text-red-400 hover:text-red-300"
                  >
                    <Trash2 className="w-4 h-4" />
                  </Button>
                </div>

                <div className="space-y-4">
                  <Input
                    label="Project Name *"
                    placeholder="e.g. PaperFox Resume Platform"
                    value={item.name}
                    onChange={(e) => updateProject(idx, "name", e.target.value)}
                  />

                  {/* Project Description Source Options */}
                  <div className="space-y-3 pt-1">
                    <label className="block text-xs font-medium text-slate-300 tracking-wide uppercase">
                      Project Description Source
                    </label>
                    
                    <div className="grid grid-cols-2 gap-3 max-w-md">
                      <button
                        type="button"
                        onClick={() => updateProject(idx, "description_source", "self")}
                        className={`flex items-center justify-center gap-2 py-2.5 px-4 rounded-lg border text-xs font-semibold transition-all ${
                          currentSource === "self"
                            ? "border-amber-500 bg-amber-500/10 text-amber-300 shadow-sm"
                            : "border-slate-800 bg-slate-950/60 text-slate-400 hover:bg-slate-800/60 hover:text-slate-200"
                        }`}
                      >
                        <User className="w-4 h-4" /> By Self
                      </button>

                      <button
                        type="button"
                        onClick={() => {
                          updateProject(idx, "description_source", "ai");
                          if (!activePrompts[idx]) {
                            handleGeneratePrompt(idx, item);
                          }
                        }}
                        className={`flex items-center justify-center gap-2 py-2.5 px-4 rounded-lg border text-xs font-semibold transition-all ${
                          currentSource === "ai"
                            ? "border-indigo-500 bg-indigo-500/10 text-indigo-300 shadow-sm"
                            : "border-slate-800 bg-slate-950/60 text-slate-400 hover:bg-slate-800/60 hover:text-slate-200"
                        }`}
                      >
                        <Sparkles className="w-4 h-4" /> By AI
                      </button>
                    </div>

                    {/* Source explanatory text */}
                    <p className="text-xs text-slate-400">
                      {currentSource === "self"
                        ? "Describe your project manually using your own details."
                        : "Generate a universal codebase-analysis prompt and use it with your preferred coding AI. The AI can inspect your actual project and return a detailed technical analysis."}
                    </p>

                    {/* By Self Flow */}
                    {currentSource === "self" && (
                      <div className="space-y-1.5 pt-1">
                        <label className="block text-xs font-medium text-slate-300 tracking-wide uppercase">
                          Manual Description
                        </label>
                        <textarea
                          rows={3}
                          placeholder="Brief summary of the project architecture, target problem, and impact..."
                          value={item.description || ""}
                          onChange={(e) => updateProject(idx, "description", e.target.value)}
                          className="w-full px-3.5 py-2.5 bg-slate-900/80 border border-slate-800 text-slate-100 placeholder-slate-500 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-amber-500/50 focus:border-amber-500"
                        />
                      </div>
                    )}

                    {/* By AI Flow */}
                    {currentSource === "ai" && (
                      <div className="space-y-4 pt-2 rounded-lg border border-indigo-500/20 bg-indigo-950/20 p-4">
                        <div className="flex flex-wrap items-center justify-between gap-2">
                          <Button
                            type="button"
                            variant="outline"
                            size="sm"
                            onClick={() => handleGeneratePrompt(idx, item)}
                            className="border-indigo-500/40 text-indigo-300 hover:bg-indigo-500/20"
                          >
                            <Sparkles className="w-4 h-4 mr-2" /> Generate Universal AI Analysis Prompt
                          </Button>
                        </div>

                        {generatedPrompt && (
                          <div className="space-y-2">
                            <p className="text-xs text-indigo-300 font-medium">
                              Copy this prompt and paste it into your preferred coding AI while the project is open.
                            </p>
                            <div className="relative">
                              <textarea
                                rows={8}
                                readOnly
                                value={generatedPrompt}
                                className="w-full px-3.5 py-2.5 bg-slate-950 border border-indigo-900/50 text-slate-300 rounded-lg text-xs font-mono focus:outline-none select-all"
                              />
                              <Button
                                type="button"
                                size="sm"
                                variant="secondary"
                                onClick={() => handleCopyPrompt(idx, generatedPrompt)}
                                className="absolute top-2 right-2 bg-slate-800/90 text-xs text-indigo-300 hover:bg-slate-700"
                              >
                                {copiedIndex === idx ? (
                                  <>
                                    <Check className="w-3.5 h-3.5 mr-1 text-green-400" /> Copied!
                                  </>
                                ) : (
                                  <>
                                    <Copy className="w-3.5 h-3.5 mr-1" /> Copy Prompt
                                  </>
                                )}
                              </Button>
                            </div>
                          </div>
                        )}

                        <div className="space-y-1.5 pt-2">
                          <label className="block text-xs font-semibold text-slate-200 uppercase flex items-center gap-1.5">
                            <FileText className="w-3.5 h-3.5 text-indigo-400" /> Paste AI Analysis Result
                          </label>
                          <p className="text-xs text-slate-400">
                            Paste the plain-text analysis generated by your coding AI. PaperFox will use this information for future project understanding and job-specific resume optimization.
                          </p>
                          <textarea
                            rows={6}
                            placeholder="Paste the plain-text response returned by your coding AI here..."
                            value={item.ai_analysis_text || ""}
                            onChange={(e) => updateProject(idx, "ai_analysis_text", e.target.value)}
                            className="w-full px-3.5 py-2.5 bg-slate-950 border border-slate-800 text-slate-100 placeholder-slate-600 rounded-lg text-xs font-mono focus:outline-none focus:ring-2 focus:ring-indigo-500/50 focus:border-indigo-500"
                          />
                        </div>
                      </div>
                    )}
                  </div>

                  <Input
                    label="Technologies Used (comma separated)"
                    placeholder="e.g. Next.js, FastAPI, Python, MongoDB, Tailwind"
                    value={item.technologies?.join(", ") || ""}
                    onChange={(e) =>
                      updateProject(
                        idx,
                        "technologies",
                        e.target.value.split(",").map((s) => s.trim()).filter(Boolean)
                      )
                    }
                  />

                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <Input
                      label="Project Demo / Live URL"
                      placeholder="https://myproject.com"
                      value={item.project_url || ""}
                      onChange={(e) => updateProject(idx, "project_url", e.target.value)}
                    />
                    <Input
                      label="Public GitHub URL"
                      placeholder="https://github.com/user/project"
                      value={item.github_url || ""}
                      onChange={(e) => updateProject(idx, "github_url", e.target.value)}
                    />
                    <Input
                      label="Repository / Source Code URL"
                      placeholder="https://gitlab.com/user/repo"
                      value={item.repository_url || ""}
                      onChange={(e) => updateProject(idx, "repository_url", e.target.value)}
                    />
                  </div>
                </div>
              </Card>
            );
          })}

          <Button type="button" variant="outline" size="sm" onClick={addProject} className="w-full">
            <Plus className="w-4 h-4 mr-2" /> Add Another Project
          </Button>
        </div>
      )}
    </div>
  );
};


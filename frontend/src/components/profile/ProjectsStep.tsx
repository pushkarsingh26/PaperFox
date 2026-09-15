"use client";

import React from "react";
import { Project } from "@/types/profile";
import { Input } from "@/components/ui/Input";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { FolderGit2, Plus, Trash2 } from "lucide-react";

interface ProjectsStepProps {
  projects: Project[];
  onChangeProjects: (items: Project[]) => void;
}

export const ProjectsStep: React.FC<ProjectsStepProps> = ({
  projects,
  onChangeProjects,
}) => {
  const addProject = () => {
    onChangeProjects([
      ...projects,
      {
        name: "",
        description: "",
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
          {projects.map((item, idx) => (
            <Card key={idx} className="p-6 space-y-4 relative border-slate-800 bg-slate-900/80">
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

                <div className="space-y-1.5">
                  <label className="block text-xs font-medium text-slate-300 tracking-wide uppercase">
                    Description *
                  </label>
                  <textarea
                    rows={3}
                    placeholder="Brief summary of the project architecture, target problem, and impact..."
                    value={item.description}
                    onChange={(e) => updateProject(idx, "description", e.target.value)}
                    className="w-full px-3.5 py-2.5 bg-slate-900/80 border border-slate-800 text-slate-100 placeholder-slate-500 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-amber-500/50 focus:border-amber-500"
                  />
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
          ))}

          <Button type="button" variant="outline" size="sm" onClick={addProject} className="w-full">
            <Plus className="w-4 h-4 mr-2" /> Add Another Project
          </Button>
        </div>
      )}
    </div>
  );
};

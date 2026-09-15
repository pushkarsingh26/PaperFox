"use client";

import React, { useState } from "react";
import { Skill } from "@/types/profile";
import { Input } from "@/components/ui/Input";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { Code2, Plus, X, AlertCircle } from "lucide-react";

interface SkillsStepProps {
  skills: Skill[];
  onChangeSkills: (items: Skill[]) => void;
}

const CATEGORIES = [
  "Programming",
  "AI / ML",
  "Frameworks",
  "Databases",
  "Cloud / Deployment",
  "Tools",
  "Other",
];

export const SkillsStep: React.FC<SkillsStepProps> = ({
  skills,
  onChangeSkills,
}) => {
  const [skillName, setSkillName] = useState("");
  const [selectedCategory, setSelectedCategory] = useState("Programming");
  const [error, setError] = useState<string | null>(null);

  const addSkill = (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    const trimmed = skillName.trim();
    if (!trimmed) return;

    const normalized = trimmed.toLowerCase();
    const exists = skills.some((s) => s.name.trim().toLowerCase() === normalized);

    if (exists) {
      setError(`Skill "${trimmed}" is already added.`);
      return;
    }

    onChangeSkills([
      ...skills,
      { name: trimmed, category: selectedCategory },
    ]);
    setSkillName("");
  };

  const removeSkill = (index: number) => {
    onChangeSkills(skills.filter((_, i) => i !== index));
  };

  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-xl font-bold text-white tracking-tight flex items-center gap-2">
          <Code2 className="w-5 h-5 text-amber-500" /> Structured Skills
        </h2>
        <p className="text-xs text-slate-400 mt-1">
          Add skills grouped by category. No duplicate skills are allowed.
        </p>
      </div>

      {/* Skill Input Form */}
      <Card className="p-6 space-y-4 bg-slate-900/80 border-slate-800">
        <form onSubmit={addSkill} className="space-y-4">
          {error && (
            <div className="p-3 bg-red-500/10 border border-red-500/30 rounded-lg flex items-center space-x-2 text-xs text-red-400">
              <AlertCircle className="w-4 h-4 shrink-0" />
              <span>{error}</span>
            </div>
          )}

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 items-end">
            <div className="sm:col-span-2">
              <Input
                label="Skill Name"
                placeholder="e.g. Python, React, PostgreSQL, Docker"
                value={skillName}
                onChange={(e) => {
                  setSkillName(e.target.value);
                  if (error) setError(null);
                }}
              />
            </div>

            <div className="space-y-1.5">
              <label className="block text-xs font-medium text-slate-300 tracking-wide uppercase">
                Category
              </label>
              <select
                value={selectedCategory}
                onChange={(e) => setSelectedCategory(e.target.value)}
                className="w-full px-3.5 py-2.5 bg-slate-900 border border-slate-800 text-slate-100 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-amber-500/50"
              >
                {CATEGORIES.map((cat) => (
                  <option key={cat} value={cat}>
                    {cat}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <Button type="submit" variant="primary" size="sm" className="w-full sm:w-auto">
            <Plus className="w-4 h-4 mr-2" /> Add Skill
          </Button>
        </form>
      </Card>

      {/* Categorized Skills Display */}
      <div className="space-y-6">
        {CATEGORIES.map((category) => {
          const categorySkills = skills.filter((s) => s.category === category);
          if (categorySkills.length === 0) return null;

          return (
            <div key={category} className="space-y-2.5">
              <div className="flex items-center justify-between border-b border-slate-800 pb-1.5">
                <span className="text-xs font-semibold text-slate-300 uppercase tracking-wider">
                  {category}
                </span>
                <span className="text-xs text-slate-500">
                  {categorySkills.length} skill{categorySkills.length > 1 ? "s" : ""}
                </span>
              </div>

              <div className="flex flex-wrap gap-2 pt-1">
                {categorySkills.map((skill) => {
                  const globalIdx = skills.findIndex((s) => s === skill);
                  return (
                    <Badge
                      key={skill.name}
                      variant="neutral"
                      className="px-3 py-1.5 text-xs bg-slate-800 hover:bg-slate-700 text-slate-200 border-slate-700 flex items-center space-x-1.5 group cursor-pointer"
                    >
                      <span>{skill.name}</span>
                      <button
                        type="button"
                        onClick={() => removeSkill(globalIdx)}
                        className="text-slate-400 hover:text-red-400 transition-colors"
                      >
                        <X className="w-3.5 h-3.5" />
                      </button>
                    </Badge>
                  );
                })}
              </div>
            </div>
          );
        })}

        {skills.length === 0 && (
          <p className="text-xs text-slate-500 text-center py-6">
            No skills added yet. Use the form above to add skills.
          </p>
        )}
      </div>
    </div>
  );
};

"use client";

import React, { useState } from "react";
import { Skill } from "@/types/profile";
import { Input } from "@/components/ui/Input";
import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { Code2, X, AlertCircle } from "lucide-react";

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
  const [skillInput, setSkillInput] = useState("");
  const [selectedCategory, setSelectedCategory] = useState("Programming");
  const [customCategory, setCustomCategory] = useState("");
  const [error, setError] = useState<string | null>(null);

  // Helper to commit one or more comma-separated skills
  const commitSkills = (rawText: string): boolean => {
    setError(null);
    const trimmedRaw = rawText.trim();
    if (!trimmedRaw) return true;

    // Determine category
    let categoryToUse = selectedCategory;
    if (selectedCategory === "Other") {
      const trimmedCustom = customCategory.trim();
      if (!trimmedCustom) {
        setError("Please enter a Custom Category before adding skills under 'Other'.");
        return false;
      }
      categoryToUse = trimmedCustom;
    }

    const items = rawText.split(",");
    const newSkillsToAdd: Skill[] = [];
    const currentSkills = [...skills];
    let duplicateWarning: string | null = null;

    for (const item of items) {
      const trimmedName = item.trim();
      if (!trimmedName) continue;

      const normalized = trimmedName.toLowerCase();
      const isDuplicate = currentSkills.some(
        (s) => s.name.trim().toLowerCase() === normalized
      );

      if (isDuplicate) {
        duplicateWarning = `Skill "${trimmedName}" already exists.`;
      } else {
        const newSkill: Skill = { name: trimmedName, category: categoryToUse };
        newSkillsToAdd.push(newSkill);
        currentSkills.push(newSkill);
      }
    }

    if (newSkillsToAdd.length > 0) {
      onChangeSkills(currentSkills);
    }

    if (duplicateWarning) {
      setError(duplicateWarning);
    }

    return true;
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const val = e.target.value;
    if (val.includes(",")) {
      const parts = val.split(",");
      const completePart = parts.slice(0, -1).join(",");
      const remaining = parts[parts.length - 1];

      const success = commitSkills(completePart);
      if (success) {
        setSkillInput(remaining);
      }
    } else {
      setSkillInput(val);
      if (error && !val.trim()) setError(null);
    }
  };

  const handlePaste = (e: React.ClipboardEvent<HTMLInputElement>) => {
    const pasted = e.clipboardData.getData("text");
    if (pasted.includes(",")) {
      e.preventDefault();
      const combined = skillInput + pasted;
      const parts = combined.split(",");
      const completePart = parts.slice(0, -1).join(",");
      const remaining = parts[parts.length - 1];

      const success = commitSkills(completePart);
      if (success) {
        setSkillInput(remaining);
      }
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter") {
      e.preventDefault();
      if (skillInput.trim()) {
        const success = commitSkills(skillInput);
        if (success) {
          setSkillInput("");
        }
      }
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (skillInput.trim()) {
      const success = commitSkills(skillInput);
      if (success) {
        setSkillInput("");
      }
    }
  };

  const removeSkill = (index: number) => {
    onChangeSkills(skills.filter((_, i) => i !== index));
  };

  // Group skills dynamically for display
  const usedCategories = Array.from(new Set(skills.map((s) => s.category)));
  const displayedCategories = Array.from(
    new Set([
      ...CATEGORIES.filter((c) => c !== "Other"),
      ...usedCategories,
      ...(usedCategories.includes("Other") ? ["Other"] : []),
    ])
  );

  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-xl font-bold text-white tracking-tight flex items-center gap-2">
          <Code2 className="w-5 h-5 text-amber-500" /> Structured Skills
        </h2>
        <p className="text-xs text-slate-400 mt-1">
          Add skills grouped by category. Type a comma (,) after each skill name to add it automatically.
        </p>
      </div>

      {/* Skill Input Form */}
      <Card className="p-6 space-y-4 bg-slate-900/80 border-slate-800">
        <form onSubmit={handleSubmit} className="space-y-4">
          {error && (
            <div className="p-3 bg-red-500/10 border border-red-500/30 rounded-lg flex items-center space-x-2 text-xs text-red-400">
              <AlertCircle className="w-4 h-4 shrink-0" />
              <span>{error}</span>
            </div>
          )}

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 items-start">
            <div className={selectedCategory === "Other" ? "sm:col-span-1" : "sm:col-span-2 lg:col-span-2"}>
              <Input
                label="Skill Name"
                placeholder="Type skill name and press comma e.g. Python, React,"
                value={skillInput}
                onChange={handleInputChange}
                onPaste={handlePaste}
                onKeyDown={handleKeyDown}
              />
              <p className="text-[11px] text-slate-500 mt-1">
                Press comma (,) to add skill instantly.
              </p>
            </div>

            <div className="space-y-1.5">
              <label className="block text-xs font-medium text-slate-300 tracking-wide uppercase">
                Category
              </label>
              <select
                value={selectedCategory}
                onChange={(e) => {
                  const val = e.target.value;
                  setSelectedCategory(val);
                  if (val !== "Other") {
                    setCustomCategory("");
                  }
                  if (error) setError(null);
                }}
                className="w-full px-3.5 py-2.5 bg-slate-900 border border-slate-800 text-slate-100 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-amber-500/50"
              >
                {CATEGORIES.map((cat) => (
                  <option key={cat} value={cat}>
                    {cat}
                  </option>
                ))}
              </select>
            </div>

            {selectedCategory === "Other" && (
              <div className="space-y-1.5 sm:col-span-2 lg:col-span-1">
                <Input
                  label="Custom Category"
                  placeholder="Write your own category"
                  value={customCategory}
                  onChange={(e) => {
                    setCustomCategory(e.target.value);
                    if (error) setError(null);
                  }}
                />
              </div>
            )}
          </div>
        </form>
      </Card>

      {/* Categorized Skills Display */}
      <div className="space-y-6">
        {displayedCategories.map((category) => {
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
                      key={`${skill.category}-${skill.name}`}
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

"use client";

import React, { useState } from "react";
import { CandidateType, Internship, WorkExperience } from "@/types/profile";
import { Input } from "@/components/ui/Input";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { Briefcase, Plus, Trash2, CheckCircle2, Building2 } from "lucide-react";

interface ExperienceStepProps {
  candidateType: CandidateType;
  internships: Internship[];
  experience: WorkExperience[];
  onChangeInternships: (items: Internship[]) => void;
  onChangeExperience: (items: WorkExperience[]) => void;
}

export const ExperienceStep: React.FC<ExperienceStepProps> = ({
  candidateType,
  internships,
  experience,
  onChangeInternships,
  onChangeExperience,
}) => {
  const [hasInternship, setHasInternship] = useState<boolean>(
    internships.length > 0
  );

  // Handlers for Internships
  const addInternship = () => {
    onChangeInternships([
      ...internships,
      {
        company: "",
        role: "",
        location: "",
        start_date: "",
        end_date: "",
        is_current: false,
        description: "",
      },
    ]);
  };

  const updateInternship = (index: number, field: keyof Internship, value: any) => {
    const updated = [...internships];
    updated[index] = { ...updated[index], [field]: value };
    onChangeInternships(updated);
  };

  const removeInternship = (index: number) => {
    const updated = internships.filter((_, i) => i !== index);
    onChangeInternships(updated);
    if (updated.length === 0) setHasInternship(false);
  };

  // Handlers for Work Experience
  const addExperience = () => {
    onChangeExperience([
      ...experience,
      {
        company: "",
        role: "",
        location: "",
        start_date: "",
        end_date: "",
        is_current: false,
        description: "",
      },
    ]);
  };

  const updateExperience = (index: number, field: keyof WorkExperience, value: any) => {
    const updated = [...experience];
    updated[index] = { ...updated[index], [field]: value };
    onChangeExperience(updated);
  };

  const removeExperience = (index: number) => {
    onChangeExperience(experience.filter((_, i) => i !== index));
  };

  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-xl font-bold text-white tracking-tight flex items-center gap-2">
          <Briefcase className="w-5 h-5 text-amber-500" />{" "}
          {candidateType === "fresher" ? "Internship Experience" : "Work Experience"}
        </h2>
        <p className="text-xs text-slate-400 mt-1">
          {candidateType === "fresher"
            ? "Record any software or industry internships (optional for freshers)."
            : "Record your full-time industry roles and achievements."}
        </p>
      </div>

      {/* Fresher Flow */}
      {candidateType === "fresher" && (
        <div className="space-y-6">
          <Card className="bg-slate-900/40 p-5 space-y-4">
            <label className="block text-sm font-semibold text-slate-200">
              Do you have internship experience to list?
            </label>
            <div className="flex items-center space-x-4">
              <Button
                type="button"
                variant={hasInternship ? "primary" : "outline"}
                size="sm"
                onClick={() => {
                  setHasInternship(true);
                  if (internships.length === 0) addInternship();
                }}
              >
                Yes, I have internships
              </Button>
              <Button
                type="button"
                variant={!hasInternship ? "secondary" : "outline"}
                size="sm"
                onClick={() => {
                  setHasInternship(false);
                  onChangeInternships([]);
                }}
              >
                No internships
              </Button>
            </div>
          </Card>

          {!hasInternship && (
            <div className="p-4 bg-emerald-500/10 border border-emerald-500/20 rounded-xl flex items-center space-x-3 text-xs text-emerald-400">
              <CheckCircle2 className="w-4 h-4 shrink-0" />
              <span>
                Internship requirement marked satisfied by choice. Your profile completion percentage will be normalized over your other sections.
              </span>
            </div>
          )}

          {hasInternship && (
            <div className="space-y-6">
              {internships.map((item, idx) => (
                <Card key={idx} className="p-6 space-y-4 relative border-slate-800 bg-slate-900/80">
                  <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                    <span className="text-xs font-semibold text-amber-400 uppercase tracking-wider flex items-center gap-1.5">
                      <Building2 className="w-3.5 h-3.5" /> Internship #{idx + 1}
                    </span>
                    <Button
                      type="button"
                      variant="ghost"
                      size="sm"
                      onClick={() => removeInternship(idx)}
                      className="text-red-400 hover:text-red-300"
                    >
                      <Trash2 className="w-4 h-4" />
                    </Button>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <Input
                      label="Company Name *"
                      placeholder="e.g. Acme Corp"
                      value={item.company}
                      onChange={(e) => updateInternship(idx, "company", e.target.value)}
                    />
                    <Input
                      label="Role / Title *"
                      placeholder="e.g. Software Engineering Intern"
                      value={item.role}
                      onChange={(e) => updateInternship(idx, "role", e.target.value)}
                    />
                    <Input
                      label="Location"
                      placeholder="e.g. San Francisco, CA (or Remote)"
                      value={item.location || ""}
                      onChange={(e) => updateInternship(idx, "location", e.target.value)}
                    />
                    <div className="flex gap-3">
                      <Input
                        label="Start Date *"
                        type="month"
                        value={item.start_date}
                        onChange={(e) => updateInternship(idx, "start_date", e.target.value)}
                      />
                      {!item.is_current && (
                        <Input
                          label="End Date"
                          type="month"
                          value={item.end_date || ""}
                          onChange={(e) => updateInternship(idx, "end_date", e.target.value)}
                        />
                      )}
                    </div>
                  </div>

                  <div className="flex items-center space-x-2 pt-1">
                    <input
                      type="checkbox"
                      id={`int-curr-${idx}`}
                      checked={item.is_current || false}
                      onChange={(e) => updateInternship(idx, "is_current", e.target.checked)}
                      className="rounded border-slate-700 bg-slate-950 text-amber-500 focus:ring-amber-500"
                    />
                    <label htmlFor={`int-curr-${idx}`} className="text-xs text-slate-300 cursor-pointer">
                      Currently working here
                    </label>
                  </div>
                </Card>
              ))}

              <Button type="button" variant="outline" size="sm" onClick={addInternship} className="w-full">
                <Plus className="w-4 h-4 mr-2" /> Add Another Internship
              </Button>
            </div>
          )}
        </div>
      )}

      {/* Experienced Flow */}
      {candidateType === "experienced" && (
        <div className="space-y-6">
          {experience.map((item, idx) => (
            <Card key={idx} className="p-6 space-y-4 relative border-slate-800 bg-slate-900/80">
              <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                <span className="text-xs font-semibold text-amber-400 uppercase tracking-wider flex items-center gap-1.5">
                  <Building2 className="w-3.5 h-3.5" /> Work Experience #{idx + 1}
                </span>
                <Button
                  type="button"
                  variant="ghost"
                  size="sm"
                  onClick={() => removeExperience(idx)}
                  className="text-red-400 hover:text-red-300"
                >
                  <Trash2 className="w-4 h-4" />
                </Button>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <Input
                  label="Company Name *"
                  placeholder="e.g. Stripe"
                  value={item.company}
                  onChange={(e) => updateExperience(idx, "company", e.target.value)}
                />
                <Input
                  label="Job Title *"
                  placeholder="e.g. Senior Backend Engineer"
                  value={item.role}
                  onChange={(e) => updateExperience(idx, "role", e.target.value)}
                />
                <Input
                  label="Location"
                  placeholder="e.g. New York, NY"
                  value={item.location || ""}
                  onChange={(e) => updateExperience(idx, "location", e.target.value)}
                />
                <div className="flex gap-3">
                  <Input
                    label="Start Date *"
                    type="month"
                    value={item.start_date}
                    onChange={(e) => updateExperience(idx, "start_date", e.target.value)}
                  />
                  {!item.is_current && (
                    <Input
                      label="End Date"
                      type="month"
                      value={item.end_date || ""}
                      onChange={(e) => updateExperience(idx, "end_date", e.target.value)}
                    />
                  )}
                </div>
              </div>

              <div className="flex items-center space-x-2 pt-1">
                <input
                  type="checkbox"
                  id={`exp-curr-${idx}`}
                  checked={item.is_current || false}
                  onChange={(e) => updateExperience(idx, "is_current", e.target.checked)}
                  className="rounded border-slate-700 bg-slate-950 text-amber-500 focus:ring-amber-500"
                />
                <label htmlFor={`exp-curr-${idx}`} className="text-xs text-slate-300 cursor-pointer">
                  Currently working in this role
                </label>
              </div>
            </Card>
          ))}

          <Button type="button" variant="outline" size="sm" onClick={addExperience} className="w-full">
            <Plus className="w-4 h-4 mr-2" /> Add Work Experience Entry
          </Button>
        </div>
      )}
    </div>
  );
};

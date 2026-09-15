"use client";

import React from "react";
import { Education } from "@/types/profile";
import { Input } from "@/components/ui/Input";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { GraduationCap, Plus, Trash2 } from "lucide-react";

interface EducationStepProps {
  education: Education[];
  onChangeEducation: (items: Education[]) => void;
}

export const EducationStep: React.FC<EducationStepProps> = ({
  education,
  onChangeEducation,
}) => {
  const addEducation = () => {
    onChangeEducation([
      ...education,
      {
        institution: "",
        degree: "",
        field_of_study: "",
        location: "",
        start_date: "",
        end_date: "",
        grade: "",
      },
    ]);
  };

  const updateEducation = (index: number, field: keyof Education, value: any) => {
    const updated = [...education];
    updated[index] = { ...updated[index], [field]: value };
    onChangeEducation(updated);
  };

  const removeEducation = (index: number) => {
    onChangeEducation(education.filter((_, i) => i !== index));
  };

  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-xl font-bold text-white tracking-tight flex items-center gap-2">
          <GraduationCap className="w-5 h-5 text-amber-500" /> Education History
        </h2>
        <p className="text-xs text-slate-400 mt-1">
          Record your academic qualifications, degrees, and institutions.
        </p>
      </div>

      {education.length === 0 ? (
        <Card className="p-8 text-center space-y-4 border-dashed border-slate-800 bg-slate-900/30">
          <GraduationCap className="w-10 h-10 text-slate-600 mx-auto" />
          <p className="text-sm text-slate-400">No education entries added yet.</p>
          <Button type="button" variant="primary" size="sm" onClick={addEducation}>
            <Plus className="w-4 h-4 mr-2" /> Add First Education Entry
          </Button>
        </Card>
      ) : (
        <div className="space-y-6">
          {education.map((item, idx) => (
            <Card key={idx} className="p-6 space-y-4 relative border-slate-800 bg-slate-900/80">
              <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                <span className="text-xs font-semibold text-amber-400 uppercase tracking-wider flex items-center gap-1.5">
                  <GraduationCap className="w-3.5 h-3.5" /> Education #{idx + 1}
                </span>
                <Button
                  type="button"
                  variant="ghost"
                  size="sm"
                  onClick={() => removeEducation(idx)}
                  className="text-red-400 hover:text-red-300"
                >
                  <Trash2 className="w-4 h-4" />
                </Button>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <Input
                  label="Institution / University *"
                  placeholder="e.g. Stanford University"
                  value={item.institution}
                  onChange={(e) => updateEducation(idx, "institution", e.target.value)}
                />
                <Input
                  label="Degree *"
                  placeholder="e.g. Bachelor of Science (B.S.)"
                  value={item.degree}
                  onChange={(e) => updateEducation(idx, "degree", e.target.value)}
                />
                <Input
                  label="Field of Study *"
                  placeholder="e.g. Computer Science"
                  value={item.field_of_study}
                  onChange={(e) => updateEducation(idx, "field_of_study", e.target.value)}
                />
                <Input
                  label="Location"
                  placeholder="e.g. Stanford, CA"
                  value={item.location || ""}
                  onChange={(e) => updateEducation(idx, "location", e.target.value)}
                />
                <Input
                  label="Start Date *"
                  type="month"
                  value={item.start_date}
                  onChange={(e) => updateEducation(idx, "start_date", e.target.value)}
                />
                <Input
                  label="End Date / Expected Graduation"
                  type="month"
                  value={item.end_date || ""}
                  onChange={(e) => updateEducation(idx, "end_date", e.target.value)}
                />
                <Input
                  label="Grade / GPA"
                  placeholder="e.g. 3.8 / 4.0 or First Class Honors"
                  value={item.grade || ""}
                  onChange={(e) => updateEducation(idx, "grade", e.target.value)}
                />
              </div>
            </Card>
          ))}

          <Button type="button" variant="outline" size="sm" onClick={addEducation} className="w-full">
            <Plus className="w-4 h-4 mr-2" /> Add Another Education Entry
          </Button>
        </div>
      )}
    </div>
  );
};

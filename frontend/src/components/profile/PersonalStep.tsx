"use client";

import React from "react";
import { CandidateType, PersonalDetails } from "@/types/profile";
import { Input } from "@/components/ui/Input";
import { Card } from "@/components/ui/Card";
import { User, Briefcase, GraduationCap, Link as LinkIcon, Phone } from "lucide-react";
import { clsx } from "clsx";

interface PersonalStepProps {
  personal: PersonalDetails;
  candidateType: CandidateType;
  onChangePersonal: (details: PersonalDetails) => void;
  onChangeType: (type: CandidateType) => void;
  userEmail?: string;
}

export const PersonalStep: React.FC<PersonalStepProps> = ({
  personal,
  candidateType,
  onChangePersonal,
  onChangeType,
  userEmail,
}) => {
  const handleChange = (field: keyof PersonalDetails, value: string) => {
    onChangePersonal({ ...personal, [field]: value });
  };

  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-xl font-bold text-white tracking-tight flex items-center gap-2">
          <User className="w-5 h-5 text-amber-500" /> Personal Details & Candidate Type
        </h2>
        <p className="text-xs text-slate-400 mt-1">
          Enter your fundamental contact links and professional classification.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Input
          label="Full Name *"
          placeholder="e.g. Alex Johnson"
          value={personal.full_name || ""}
          onChange={(e) => handleChange("full_name", e.target.value)}
          required
        />

        <div className="w-full space-y-1.5">
          <label className="block text-xs font-medium text-slate-400 tracking-wide uppercase">
            Account Email (Authoritative)
          </label>
          <input
            type="email"
            value={userEmail || ""}
            disabled
            className="w-full px-3.5 py-2.5 bg-slate-900/40 border border-slate-800 text-slate-400 rounded-lg text-sm cursor-not-allowed"
          />
        </div>

        <Input
          label="Phone Number"
          placeholder="+1 (555) 000-0000"
          value={personal.phone || ""}
          onChange={(e) => handleChange("phone", e.target.value)}
        />

        <Input
          label="Portfolio / Personal Website"
          placeholder="https://alexjohnson.dev"
          value={personal.portfolio_url || ""}
          onChange={(e) => handleChange("portfolio_url", e.target.value)}
        />

        <Input
          label="LinkedIn Profile URL"
          placeholder="https://linkedin.com/in/alexjohnson"
          value={personal.linkedin_url || ""}
          onChange={(e) => handleChange("linkedin_url", e.target.value)}
        />

        <Input
          label="GitHub Profile URL"
          placeholder="https://github.com/alexjohnson"
          value={personal.github_url || ""}
          onChange={(e) => handleChange("github_url", e.target.value)}
        />
      </div>

      <div className="pt-4 border-t border-slate-800">
        <label className="block text-xs font-medium text-slate-300 tracking-wide uppercase mb-3">
          Candidate Classification *
        </label>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <Card
            onClick={() => onChangeType("fresher")}
            className={clsx(
              "cursor-pointer transition-all duration-200 border-2 p-5 flex items-start space-x-4",
              candidateType === "fresher"
                ? "border-amber-500 bg-amber-500/10"
                : "border-slate-800 hover:border-slate-700 bg-slate-900/40"
            )}
          >
            <div className="w-10 h-10 rounded-lg bg-amber-500/20 text-amber-400 flex items-center justify-center shrink-0">
              <GraduationCap className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-sm font-bold text-white">Fresher / Student</h3>
              <p className="text-xs text-slate-400 mt-1 leading-relaxed">
                Recent graduate or student. Work experience is optional or focused on internships.
              </p>
            </div>
          </Card>

          <Card
            onClick={() => onChangeType("experienced")}
            className={clsx(
              "cursor-pointer transition-all duration-200 border-2 p-5 flex items-start space-x-4",
              candidateType === "experienced"
                ? "border-amber-500 bg-amber-500/10"
                : "border-slate-800 hover:border-slate-700 bg-slate-900/40"
            )}
          >
            <div className="w-10 h-10 rounded-lg bg-amber-500/20 text-amber-400 flex items-center justify-center shrink-0">
              <Briefcase className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-sm font-bold text-white">Experienced Professional</h3>
              <p className="text-xs text-slate-400 mt-1 leading-relaxed">
                Prior full-time work experience in relevant industry roles.
              </p>
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
};

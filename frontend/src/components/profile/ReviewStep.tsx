"use client";

import React from "react";
import Link from "next/link";
import { CandidateProfile } from "@/types/profile";
import { Card } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Badge } from "@/components/ui/Badge";
import {
  CheckCircle2,
  Edit2,
  User,
  Briefcase,
  GraduationCap,
  FolderGit2,
  Code2,
  Award,
  FileText,
  ExternalLink,
} from "lucide-react";

interface ReviewStepProps {
  profile: CandidateProfile;
  userEmail?: string;
  onGoToStep: (stepIndex: number) => void;
  onComplete: () => Promise<void>;
  isSaving: boolean;
}

export const ReviewStep: React.FC<ReviewStepProps> = ({
  profile,
  userEmail,
  onGoToStep,
  onComplete,
  isSaving,
}) => {
  const isComplete = profile.profile_status === "complete";

  return (
    <div className="space-y-8">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-6">
        <div>
          <h2 className="text-xl font-bold text-white tracking-tight flex items-center gap-2">
            <CheckCircle2 className="w-5 h-5 text-amber-500" /> Review Candidate Profile
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Review your entered background before saving. You can edit any section at any time.
          </p>
        </div>

        <div className="flex items-center space-x-3">
          <Badge
            variant={isComplete ? "success" : "warning"}
            className="px-3 py-1 text-xs"
          >
            {isComplete ? "Profile Complete" : "Draft Status"}
          </Badge>
          <span className="text-xs font-mono font-bold text-amber-400">
            {profile.completion_percentage}% Complete
          </span>
        </div>
      </div>

      {isComplete && (
        <div className="p-5 bg-emerald-500/10 border border-emerald-500/30 rounded-xl flex flex-col sm:flex-row sm:items-center justify-between gap-4 shadow-lg shadow-emerald-950/20">
          <div className="flex items-start sm:items-center space-x-3 text-xs text-emerald-400">
            <CheckCircle2 className="w-6 h-6 shrink-0 text-emerald-400 mt-0.5 sm:mt-0" />
            <div>
              <p className="font-bold text-sm text-emerald-300">Master Candidate Profile Complete!</p>
              <p className="text-xs text-emerald-200/80 mt-0.5">
                Your profile is saved and your 1-page Base Resume is ready to view, order, and compile.
              </p>
            </div>
          </div>
          <Link href="/dashboard/resume">
            <Button
              type="button"
              variant="primary"
              size="md"
              className="bg-emerald-600 hover:bg-emerald-500 text-white font-semibold whitespace-nowrap shadow-md"
            >
              <FileText className="w-4 h-4 mr-2" /> View Base Resume
            </Button>
          </Link>
        </div>
      )}

      {/* Section 1: Personal Details */}
      <Card className="p-6 space-y-4 bg-slate-900/80 border-slate-800">
        <div className="flex items-center justify-between border-b border-slate-800 pb-3">
          <h3 className="text-sm font-bold text-white flex items-center gap-2">
            <User className="w-4 h-4 text-amber-500" /> Personal Details & Type
          </h3>
          <Button type="button" variant="ghost" size="sm" onClick={() => onGoToStep(0)}>
            <Edit2 className="w-3.5 h-3.5 mr-1" /> Edit
          </Button>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
          <div>
            <span className="text-slate-500 block uppercase font-medium">Full Name</span>
            <span className="text-slate-200 font-semibold">{profile.personal_details.full_name || "Not provided"}</span>
          </div>
          <div>
            <span className="text-slate-500 block uppercase font-medium">Account Email</span>
            <span className="text-slate-200 font-semibold">{userEmail}</span>
          </div>
          <div>
            <span className="text-slate-500 block uppercase font-medium">Phone Number</span>
            <span className="text-slate-200">{profile.personal_details.phone || "Not provided"}</span>
          </div>
          <div>
            <span className="text-slate-500 block uppercase font-medium">Classification</span>
            <span className="text-amber-400 font-semibold uppercase">{profile.candidate_type}</span>
          </div>

          <div>
            <span className="text-slate-500 block uppercase font-medium">GitHub Profile</span>
            {profile.personal_details.github_url ? (
              <a
                href={profile.personal_details.github_url}
                target="_blank"
                rel="noreferrer"
                className="text-amber-400 hover:underline inline-flex items-center gap-1 break-all"
              >
                {profile.personal_details.github_url}
                <ExternalLink className="w-3 h-3 shrink-0" />
              </a>
            ) : (
              <span className="text-slate-400 italic">Not provided</span>
            )}
          </div>

          <div>
            <span className="text-slate-500 block uppercase font-medium">LinkedIn Profile</span>
            {profile.personal_details.linkedin_url ? (
              <a
                href={profile.personal_details.linkedin_url}
                target="_blank"
                rel="noreferrer"
                className="text-amber-400 hover:underline inline-flex items-center gap-1 break-all"
              >
                {profile.personal_details.linkedin_url}
                <ExternalLink className="w-3 h-3 shrink-0" />
              </a>
            ) : (
              <span className="text-slate-400 italic">Not provided</span>
            )}
          </div>

          <div className="sm:col-span-2">
            <span className="text-slate-500 block uppercase font-medium">Portfolio / Personal Website</span>
            {profile.personal_details.portfolio_url ? (
              <a
                href={profile.personal_details.portfolio_url}
                target="_blank"
                rel="noreferrer"
                className="text-amber-400 hover:underline inline-flex items-center gap-1 break-all"
              >
                {profile.personal_details.portfolio_url}
                <ExternalLink className="w-3 h-3 shrink-0" />
              </a>
            ) : (
              <span className="text-slate-400 italic">Not provided</span>
            )}
          </div>
        </div>
      </Card>

      {/* Section 2: Experience / Internships */}
      <Card className="p-6 space-y-4 bg-slate-900/80 border-slate-800">
        <div className="flex items-center justify-between border-b border-slate-800 pb-3">
          <h3 className="text-sm font-bold text-white flex items-center gap-2">
            <Briefcase className="w-4 h-4 text-amber-500" />{" "}
            {profile.candidate_type === "fresher" ? "Internships" : "Work Experience"}
          </h3>
          <Button type="button" variant="ghost" size="sm" onClick={() => onGoToStep(1)}>
            <Edit2 className="w-3.5 h-3.5 mr-1" /> Edit
          </Button>
        </div>

        {profile.candidate_type === "fresher" ? (
          profile.internships.length === 0 ? (
            <p className="text-xs text-slate-400 italic">No internships listed (requirement satisfied by choice).</p>
          ) : (
            <div className="space-y-3">
              {profile.internships.map((int, i) => (
                <div key={i} className="text-xs space-y-1 border-l-2 border-amber-500/40 pl-3">
                  <p className="font-bold text-white">{int.role} @ {int.company}</p>
                  <p className="text-slate-400">{int.start_date} – {int.is_current ? "Present" : int.end_date || "N/A"}</p>
                </div>
              ))}
            </div>
          )
        ) : profile.experience.length === 0 ? (
          <p className="text-xs text-slate-400 italic">No work experience listed.</p>
        ) : (
          <div className="space-y-3">
            {profile.experience.map((exp, i) => (
              <div key={i} className="text-xs space-y-1 border-l-2 border-amber-500/40 pl-3">
                <p className="font-bold text-white">{exp.role} @ {exp.company}</p>
                <p className="text-slate-400">{exp.start_date} – {exp.is_current ? "Present" : exp.end_date || "N/A"}</p>
              </div>
            ))}
          </div>
        )}
      </Card>

      {/* Section 3: Education */}
      <Card className="p-6 space-y-4 bg-slate-900/80 border-slate-800">
        <div className="flex items-center justify-between border-b border-slate-800 pb-3">
          <h3 className="text-sm font-bold text-white flex items-center gap-2">
            <GraduationCap className="w-4 h-4 text-amber-500" /> Education ({profile.education.length})
          </h3>
          <Button type="button" variant="ghost" size="sm" onClick={() => onGoToStep(2)}>
            <Edit2 className="w-3.5 h-3.5 mr-1" /> Edit
          </Button>
        </div>

        {profile.education.length === 0 ? (
          <p className="text-xs text-slate-400 italic">No education entries listed.</p>
        ) : (
          <div className="space-y-3">
            {profile.education.map((edu, i) => (
              <div key={i} className="text-xs space-y-1 border-l-2 border-amber-500/40 pl-3">
                <p className="font-bold text-white">{edu.degree} in {edu.field_of_study}</p>
                <p className="text-slate-300">{edu.institution} {edu.grade ? `(${edu.grade})` : ""}</p>
                <p className="text-slate-400">{edu.start_date} – {edu.end_date || "Present"}</p>
              </div>
            ))}
          </div>
        )}
      </Card>

      {/* Section 4: Projects */}
      <Card className="p-6 space-y-4 bg-slate-900/80 border-slate-800">
        <div className="flex items-center justify-between border-b border-slate-800 pb-3">
          <h3 className="text-sm font-bold text-white flex items-center gap-2">
            <FolderGit2 className="w-4 h-4 text-amber-500" /> Projects ({profile.projects.length})
          </h3>
          <Button type="button" variant="ghost" size="sm" onClick={() => onGoToStep(3)}>
            <Edit2 className="w-3.5 h-3.5 mr-1" /> Edit
          </Button>
        </div>

        {profile.projects.length === 0 ? (
          <p className="text-xs text-slate-400 italic">No projects added.</p>
        ) : (
          <div className="space-y-3">
            {profile.projects.map((proj, i) => (
              <div key={i} className="text-xs space-y-1 border-l-2 border-amber-500/40 pl-3">
                <p className="font-bold text-white">{proj.name}</p>
                {proj.technologies && proj.technologies.length > 0 && (
                  <p className="text-amber-400 font-mono text-[11px]">
                    {proj.technologies.join(", ")}
                  </p>
                )}
                {proj.description && <p className="text-slate-400">{proj.description}</p>}
              </div>
            ))}
          </div>
        )}
      </Card>

      {/* Section 5: Skills */}
      <Card className="p-6 space-y-4 bg-slate-900/80 border-slate-800">
        <div className="flex items-center justify-between border-b border-slate-800 pb-3">
          <h3 className="text-sm font-bold text-white flex items-center gap-2">
            <Code2 className="w-4 h-4 text-amber-500" /> Skills ({profile.skills.length})
          </h3>
          <Button type="button" variant="ghost" size="sm" onClick={() => onGoToStep(4)}>
            <Edit2 className="w-3.5 h-3.5 mr-1" /> Edit
          </Button>
        </div>

        {profile.skills.length === 0 ? (
          <p className="text-xs text-slate-400 italic">No skills listed.</p>
        ) : (
          <div className="flex flex-wrap gap-2">
            {profile.skills.map((s) => (
              <Badge key={s.name} variant="neutral" className="text-xs">
                {s.name} ({s.category})
              </Badge>
            ))}
          </div>
        )}
      </Card>

      {/* Section 6: Certifications */}
      <Card className="p-6 space-y-4 bg-slate-900/80 border-slate-800">
        <div className="flex items-center justify-between border-b border-slate-800 pb-3">
          <h3 className="text-sm font-bold text-white flex items-center gap-2">
            <Award className="w-4 h-4 text-amber-500" /> Certifications ({profile.certifications.length})
          </h3>
          <Button type="button" variant="ghost" size="sm" onClick={() => onGoToStep(5)}>
            <Edit2 className="w-3.5 h-3.5 mr-1" /> Edit
          </Button>
        </div>

        {profile.certifications.length === 0 ? (
          <p className="text-xs text-slate-400 italic">No certifications listed.</p>
        ) : (
          <div className="space-y-2 text-xs">
            {profile.certifications.map((c, i) => (
              <p key={i} className="text-slate-300 font-medium">
                • {c.name} — <span className="text-slate-400">{c.issuer}</span>
              </p>
            ))}
          </div>
        )}
      </Card>

      {/* Final Complete Action */}
      <div className="pt-4 border-t border-slate-800 flex flex-wrap items-center justify-between gap-3">
        {isComplete ? (
          <div className="flex items-center space-x-2 text-xs text-emerald-400">
            <CheckCircle2 className="w-4 h-4" />
            <span>Profile marked complete</span>
          </div>
        ) : (
          <p className="text-xs text-slate-500">
            Review your information and complete profile to activate Base Resume.
          </p>
        )}

        <div className="flex items-center space-x-3">
          {isComplete && (
            <Link href="/dashboard/resume">
              <Button
                type="button"
                variant="secondary"
                size="lg"
                className="font-bold"
              >
                <FileText className="w-4 h-4 mr-2" /> View Base Resume
              </Button>
            </Link>
          )}

          <Button
            type="button"
            variant="primary"
            size="lg"
            onClick={onComplete}
            isLoading={isSaving}
            className="px-8 font-bold"
          >
            {isComplete ? "Update & Save Profile" : "Save & Complete Profile"}
          </Button>
        </div>
      </div>
    </div>
  );
};

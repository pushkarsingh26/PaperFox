"use client";

import React, { useEffect, useState } from "react";
import { useAuth } from "@/context/AuthContext";
import { api } from "@/lib/api";
import { CandidateProfile } from "@/types/profile";
import { PersonalStep } from "./PersonalStep";
import { ExperienceStep } from "./ExperienceStep";
import { EducationStep } from "./EducationStep";
import { ProjectsStep } from "./ProjectsStep";
import { SkillsStep } from "./SkillsStep";
import { CertificationsStep } from "./CertificationsStep";
import { ReviewStep } from "./ReviewStep";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import {
  User,
  Briefcase,
  GraduationCap,
  FolderGit2,
  Code2,
  Award,
  CheckCircle2,
  ArrowLeft,
  ArrowRight,
  Save,
  Loader2,
  AlertCircle,
} from "lucide-react";
import { clsx } from "clsx";

const STEPS = [
  { label: "Personal", icon: User },
  { label: "Experience", icon: Briefcase },
  { label: "Education", icon: GraduationCap },
  { label: "Projects", icon: FolderGit2 },
  { label: "Skills", icon: Code2 },
  { label: "Certifications", icon: Award },
  { label: "Review", icon: CheckCircle2 },
];

const initialProfile: CandidateProfile = {
  profile_status: "draft",
  personal_details: {
    full_name: "",
    phone: "",
    portfolio_url: "",
    linkedin_url: "",
    github_url: "",
  },
  candidate_type: "fresher",
  internships: [],
  experience: [],
  education: [],
  projects: [],
  skills: [],
  certifications: [],
  completion_percentage: 0,
};

export const ProfileFormShell: React.FC = () => {
  const { user } = useAuth();
  const [profile, setProfile] = useState<CandidateProfile>(initialProfile);
  const [currentStep, setCurrentStep] = useState<number>(0);
  const [loading, setLoading] = useState<boolean>(true);
  const [isSaving, setIsSaving] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [saveMessage, setSaveMessage] = useState<string | null>(null);

  // Fetch existing candidate profile on mount
  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const response = await api.get<CandidateProfile>("/profile");
        if (response.data) {
          setProfile(response.data);
        }
      } catch (err: any) {
        // 404 means no profile created yet, keep initialProfile state
      } finally {
        setLoading(false);
      }
    };
    fetchProfile();
  }, []);

  const saveProfileState = async (updatedStatus?: "draft" | "complete") => {
    setIsSaving(true);
    setError(null);
    setSaveMessage(null);

    try {
      const payload = {
        ...profile,
        profile_status: updatedStatus || profile.profile_status,
      };

      const response = await api.post<CandidateProfile>("/profile", payload);
      setProfile(response.data);
      setSaveMessage("Profile saved successfully");
      setTimeout(() => setSaveMessage(null), 3000);
    } catch (err: any) {
      const detail = err.response?.data?.detail;
      const msg = typeof detail === "string" ? detail : "Failed to save candidate profile.";
      setError(msg);
    } finally {
      setIsSaving(false);
    }
  };

  const handleNext = async () => {
    await saveProfileState("draft");
    if (currentStep < STEPS.length - 1) {
      setCurrentStep((prev) => prev + 1);
      window.scrollTo({ top: 0, behavior: "smooth" });
    }
  };

  const handleBack = () => {
    if (currentStep > 0) {
      setCurrentStep((prev) => prev - 1);
      window.scrollTo({ top: 0, behavior: "smooth" });
    }
  };

  const handleCompleteProfile = async () => {
    await saveProfileState("complete");
  };

  if (loading) {
    return (
      <div className="py-20 flex flex-col items-center justify-center space-y-4">
        <Loader2 className="w-8 h-8 text-amber-500 animate-spin" />
        <p className="text-sm text-slate-400">Loading Master Candidate Profile...</p>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Header & Progress Indicator */}
      <div className="bg-slate-900/70 border border-slate-800/80 p-6 rounded-2xl space-y-4">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl font-bold text-white tracking-tight">
              Master Candidate Profile
            </h1>
            <p className="text-xs text-slate-400 mt-1">
              Single source of truth for job-specific resume optimization.
            </p>
          </div>

          <div className="flex items-center space-x-4">
            <div className="text-right">
              <span className="text-xs text-slate-400 block font-medium">Completion Score</span>
              <span className="text-lg font-bold font-mono text-amber-400">
                {profile.completion_percentage}%
              </span>
            </div>
            <Badge
              variant={profile.profile_status === "complete" ? "success" : "warning"}
              dot
              className="px-3.5 py-1 text-xs"
            >
              {profile.profile_status === "complete" ? "Complete" : "Draft"}
            </Badge>
          </div>
        </div>

        {/* Visual Progress Bar */}
        <div className="w-full bg-slate-950/80 h-2 rounded-full overflow-hidden border border-slate-800/60">
          <div
            className="bg-gradient-to-r from-amber-500 to-amber-400 h-full rounded-full transition-all duration-500 shadow-sm shadow-amber-500/50"
            style={{ width: `${Math.min(100, Math.max(0, profile.completion_percentage))}%` }}
          />
        </div>
      </div>

      {/* Save Message & Error Notifications */}
      {error && (
        <div className="p-4 bg-red-500/10 border border-red-500/30 rounded-xl flex items-center space-x-3 text-xs text-red-400">
          <AlertCircle className="w-4 h-4 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {saveMessage && (
        <div className="p-3 bg-emerald-500/10 border border-emerald-500/20 rounded-xl flex items-center space-x-2 text-xs text-emerald-400">
          <CheckCircle2 className="w-4 h-4 shrink-0" />
          <span>{saveMessage}</span>
        </div>
      )}

      {/* Step Tabs Navigation */}
      <div className="flex items-center overflow-x-auto border-b border-slate-800 pb-2 space-x-1 no-scrollbar">
        {STEPS.map((step, idx) => {
          const Icon = step.icon;
          const isActive = currentStep === idx;
          const isCompleted = idx < currentStep;

          return (
            <button
              key={step.label}
              type="button"
              onClick={async () => {
                await saveProfileState();
                setCurrentStep(idx);
              }}
              className={clsx(
                "flex items-center space-x-2 px-4 py-2.5 rounded-lg text-xs font-medium whitespace-nowrap transition-all duration-150",
                isActive
                  ? "bg-amber-500/10 text-amber-400 border border-amber-500/30 font-bold"
                  : isCompleted
                  ? "text-slate-300 hover:bg-slate-800/40"
                  : "text-slate-500 hover:bg-slate-900/40"
              )}
            >
              <Icon className={clsx("w-3.5 h-3.5", isActive ? "text-amber-400" : "text-slate-500")} />
              <span>{step.label}</span>
            </button>
          );
        })}
      </div>

      {/* Current Step Component */}
      <Card className="p-6 md:p-8 border-slate-800 bg-slate-900/40">
        {currentStep === 0 && (
          <PersonalStep
            personal={profile.personal_details}
            candidateType={profile.candidate_type}
            onChangePersonal={(details) => setProfile({ ...profile, personal_details: details })}
            onChangeType={(type) => setProfile({ ...profile, candidate_type: type })}
            userEmail={user?.email}
          />
        )}

        {currentStep === 1 && (
          <ExperienceStep
            candidateType={profile.candidate_type}
            internships={profile.internships}
            experience={profile.experience}
            onChangeInternships={(items) => setProfile({ ...profile, internships: items })}
            onChangeExperience={(items) => setProfile({ ...profile, experience: items })}
          />
        )}

        {currentStep === 2 && (
          <EducationStep
            education={profile.education}
            onChangeEducation={(items) => setProfile({ ...profile, education: items })}
          />
        )}

        {currentStep === 3 && (
          <ProjectsStep
            projects={profile.projects}
            onChangeProjects={(items) => setProfile({ ...profile, projects: items })}
          />
        )}

        {currentStep === 4 && (
          <SkillsStep
            skills={profile.skills}
            onChangeSkills={(items) => setProfile({ ...profile, skills: items })}
          />
        )}

        {currentStep === 5 && (
          <CertificationsStep
            certifications={profile.certifications}
            onChangeCertifications={(items) => setProfile({ ...profile, certifications: items })}
          />
        )}

        {currentStep === 6 && (
          <ReviewStep
            profile={profile}
            userEmail={user?.email}
            onGoToStep={(idx) => setCurrentStep(idx)}
            onComplete={handleCompleteProfile}
            isSaving={isSaving}
          />
        )}
      </Card>

      {/* Footer Controls */}
      <div className="flex items-center justify-between pt-4 border-t border-slate-800">
        <Button
          type="button"
          variant="outline"
          size="md"
          onClick={handleBack}
          disabled={currentStep === 0 || isSaving}
        >
          <ArrowLeft className="w-4 h-4 mr-2" /> Back
        </Button>

        <div className="flex items-center space-x-3">
          <Button
            type="button"
            variant="secondary"
            size="md"
            onClick={() => saveProfileState()}
            isLoading={isSaving}
          >
            <Save className="w-4 h-4 mr-2" /> Save Progress
          </Button>

          {currentStep < STEPS.length - 1 && (
            <Button
              type="button"
              variant="primary"
              size="md"
              onClick={handleNext}
              isLoading={isSaving}
            >
              Continue <ArrowRight className="w-4 h-4 ml-2" />
            </Button>
          )}
        </div>
      </div>
    </div>
  );
};

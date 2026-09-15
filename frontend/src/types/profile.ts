export type CandidateType = "fresher" | "experienced";
export type ProfileStatus = "draft" | "complete";

export interface PersonalDetails {
  full_name: string;
  phone?: string;
  portfolio_url?: string;
  linkedin_url?: string;
  github_url?: string;
}

export interface Internship {
  id?: string;
  company: string;
  role: string;
  location?: string;
  start_date: string;
  end_date?: string;
  is_current?: boolean;
  description?: string;
  responsibilities?: string[];
  technologies?: string[];
  achievements?: string[];
}

export interface WorkExperience {
  id?: string;
  company: string;
  role: string;
  location?: string;
  start_date: string;
  end_date?: string;
  is_current?: boolean;
  description?: string;
  responsibilities?: string[];
  technologies?: string[];
  achievements?: string[];
}

export interface Education {
  id?: string;
  institution: string;
  degree: string;
  field_of_study: string;
  location?: string;
  start_date: string;
  end_date?: string;
  grade?: string;
  grade_type?: string;
  description?: string;
}

export interface ProjectEvidence {
  status?: string;
  source?: string;
  architecture?: string[];
  technologies?: string[];
  frameworks?: string[];
  APIs?: string[];
  models?: string[];
  databases?: string[];
  deployment?: string[];
  features?: string[];
  technical_details?: string[];
  verified_at?: string;
}

export interface Project {
  id?: string;
  name: string;
  description: string;
  technologies?: string[];
  features?: string[];
  responsibilities?: string[];
  achievements?: string[];
  project_url?: string;
  github_url?: string;
  repository_url?: string;
  start_date?: string;
  end_date?: string;
  evidence?: ProjectEvidence;
}

export interface Skill {
  id?: string;
  name: string;
  category: "Programming" | "AI / ML" | "Frameworks" | "Databases" | "Cloud / Deployment" | "Tools" | "Other" | string;
}

export interface Certification {
  id?: string;
  name: string;
  issuer: string;
  issue_date?: string;
  credential_id?: string;
  credential_url?: string;
  description?: string;
}

export interface CandidateProfile {
  id?: string;
  user_id?: string;
  profile_status: ProfileStatus;
  personal_details: PersonalDetails;
  candidate_type: CandidateType;
  internships: Internship[];
  experience: WorkExperience[];
  education: Education[];
  projects: Project[];
  skills: Skill[];
  certifications: Certification[];
  completion_percentage: number;
  created_at?: string;
  updated_at?: string;
}

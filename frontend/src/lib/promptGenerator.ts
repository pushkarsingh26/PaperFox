import { Project } from "@/types/profile";

export function generateUniversalProjectPrompt(project: Project): string {
  const projectName = project.name?.trim() || "Untitled Project";

  const contextLines: string[] = [];
  if (project.description?.trim()) {
    contextLines.push(`- Description: ${project.description.trim()}`);
  }

  if (project.technologies && project.technologies.length > 0) {
    contextLines.push(`- Technologies: ${project.technologies.join(", ")}`);
  }

  const repoUrl = project.repository_url || project.github_url || project.project_url;
  if (repoUrl?.trim()) {
    contextLines.push(`- Repository / Project URL: ${repoUrl.trim()}`);
  }

  if (project.features && project.features.length > 0) {
    contextLines.push(`- Known Features: ${project.features.join(", ")}`);
  }

  if (project.responsibilities && project.responsibilities.length > 0) {
    contextLines.push(`- Candidate Responsibilities: ${project.responsibilities.join(", ")}`);
  }

  const contextStr = contextLines.length > 0
    ? contextLines.join("\n")
    : "None provided. Perform a complete inspection of the current workspace codebase.";

  return `PROJECT CODEBASE ANALYSIS REQUEST

You are analyzing an existing software project for the purpose of creating an accurate technical description that may later be used for professional resume optimization.

PROJECT NAME:
${projectName}

KNOWN PROJECT CONTEXT:
${contextStr}

TASK:

Inspect the actual project/codebase available in your current workspace.

Analyze only what can be verified from the project files, source code, configuration, dependency files, documentation, deployment configuration, and other available implementation artifacts.

Do not assume that a technology, framework, API, model, database, feature, architecture pattern, or deployment method exists unless there is evidence in the codebase.

If something cannot be verified, explicitly state that it could not be verified.

ANALYZE THE PROJECT IN DETAIL:

1. Project Overview
Explain what the project does and its primary purpose.

2. Architecture
Describe the overall architecture and major components.

3. Frontend
Describe the frontend technology, structure, important components, state management, routing, and relevant implementation details.

4. Backend
Describe backend technologies, frameworks, APIs, services, business logic, and important implementation patterns.

5. AI / ML
If applicable, identify:
- models
- model providers
- inference mechanisms
- prompts
- RAG
- embeddings
- vector databases
- agents
- AI pipelines
- evaluation mechanisms

Only report what is actually present.

6. APIs and Integrations
Identify external and internal APIs, SDKs, services, authentication mechanisms, and integrations.

7. Database and Storage
Identify databases, schemas/models, storage systems, caching systems, and persistence mechanisms.

8. Authentication and Security
Identify authentication, authorization, sessions, JWT, OAuth, API-key handling, validation, security middleware, or other relevant mechanisms.

9. Technologies and Frameworks
List technologies that are actually used in the implementation.

10. Important Features
Describe the major implemented features and how they work.

11. Engineering Details
Identify technically meaningful implementation details that demonstrate engineering depth.

12. Deployment / Infrastructure
Identify deployment platforms, containers, CI/CD, environment configuration, cloud services, workers, queues, or infrastructure components if actually present.

13. Notable Engineering Decisions
Explain meaningful technical decisions visible in the codebase.

14. Project Limitations / Unverified Areas
Clearly identify anything that could not be verified.

15. Resume-Relevant Technical Highlights
Provide a concise section identifying the strongest technically verified aspects of the project that could later be useful for a professional resume.

FACTUAL GROUNDING RULES:

- Inspect the actual codebase before answering.
- Do not fabricate technologies.
- Do not fabricate metrics.
- Do not fabricate performance numbers.
- Do not fabricate users or usage statistics.
- Do not fabricate architecture.
- Do not fabricate APIs.
- Do not fabricate AI models.
- Do not fabricate deployment infrastructure.
- Do not convert assumptions into facts.
- Do not claim a feature exists simply because documentation says it should exist if the implementation cannot be verified.
- Distinguish between implemented, partially implemented, documented, and unverified functionality where appropriate.

OUTPUT FORMAT:

Return PLAIN TEXT ONLY.

Do NOT return:
- JSON
- YAML
- XML
- Markdown tables
- code blocks
- machine-readable schemas

Use clear section headings and normal readable text.

The output should be detailed enough for another AI system to reliably understand the actual technical implementation of the project.

Do not modify the project files unless explicitly requested.
`;
}

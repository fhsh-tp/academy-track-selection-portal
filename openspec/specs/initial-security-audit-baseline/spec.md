# initial-security-audit-baseline Specification

## Purpose

TBD - created by archiving change 'create-initial-security-audit-baseline'. Update Purpose after archive.

## Requirements

### Requirement: Initial Security Audit Report

The project SHALL publish a current security audit baseline under `docs/security/` that identifies the reviewed audit name, review date, branch or commit reference, scope, methodology, reviewed code areas, findings summary, remediation priorities, and references to the supporting OWASP audit artifacts used to produce the baseline.

#### Scenario: Current audit baseline is available

- **WHEN** a maintainer opens `docs/security/` after this change
- **THEN** the directory contains a current security audit baseline with the reviewed audit name, review date, branch or commit reference, scope, methodology, reviewed areas, findings summary, and remediation priorities

#### Scenario: Published baseline is traceable to supporting audit artifacts

- **WHEN** a maintainer follows the references from the published security audit baseline
- **THEN** the baseline identifies the supporting OWASP audit workspace and the related scope, plan, findings, or report artifacts for that review


<!-- @trace
source: refresh-project-security-audit-baseline
updated: 2026-04-06
code:
  - .agents/skills/spectra-discuss
  - docs/security/2026-04-06_codex_audit/README.md
  - .agents/skills/spectra-archive
  - .env.example
  - .security-audit/archive/2026-04-06-project-wide-security-audit-2026-04-06/findings/FINDING-003.md
  - .github/skills/spectra-archive/SKILL.md
  - .security-audit/archive/2026-04-06-project-wide-security-audit-2026-04-06/report-en.md
  - .github/skills/spectra-discuss/SKILL.md
  - docs/security/2026-04-06_codex_audit/initial-audit-report.md
  - .security-audit/archive/2026-04-06-project-wide-security-audit-2026-04-06/.audit.yaml
  - .agents/skills/spectra-apply
  - .github/prompts/spectra-debug.prompt.md
  - .agents/skills/spectra-audit
  - .github/prompts/spectra-discuss.prompt.md
  - .agents/skills/spectra-ask/SKILL.md
  - .github/prompts/spectra-archive.prompt.md
  - backend/main.py
  - docs/security/2026-04-05_codex_audit/findings/FINDING-001-submit-integrity-gap.md
  - .github/prompts/spectra-apply.prompt.md
  - .github/skills/spectra-debug/SKILL.md
  - .agents/skills/spectra-audit/SKILL.md
  - .agents/skills/spectra-ask
  - .security-audit/archive/2026-04-06-project-wide-security-audit-2026-04-06/findings/FINDING-001.md
  - .agents/skills/spectra-archive/SKILL.md
  - .security-audit/archive/2026-04-06-project-wide-security-audit-2026-04-06/report-tw.md
  - frontend/index.html
  - .security-audit/archive/2026-04-06-project-wide-security-audit-2026-04-06/findings/FINDING-004.md
  - .agents/skills/spectra-propose/SKILL.md
  - uv.lock
  - .security-audit/archive/2026-04-06-project-wide-security-audit-2026-04-06/plan.md
  - .security-audit/archive/2026-04-06-project-wide-security-audit-2026-04-06/scope.md
  - docs/security/2026-04-06_codex_audit/dependency-vulnerability-scan.md
  - .agents/skills/spectra-ingest/SKILL.md
  - .github/skills/spectra-propose/SKILL.md
  - .agents/skills/spectra-apply/SKILL.md
  - .github/skills/spectra-apply/SKILL.md
  - .github/prompts/spectra-propose.prompt.md
  - .agents/skills/spectra-discuss/SKILL.md
  - .security-audit/archive/2026-04-06-project-wide-security-audit-2026-04-06/tasks.md
  - .github/prompts/spectra-ingest.prompt.md
  - .agents/skills/spectra-debug
  - backend/utils/dependencies.py
  - README.md
  - .github/prompts/spectra-audit.prompt.md
  - backend/utils/email.py.bak
  - scripts/buildx.sh
  - .agents/skills/spectra-debug/SKILL.md
  - .github/prompts/spectra-ask.prompt.md
  - .github/skills/spectra-ask/SKILL.md
  - .github/skills/spectra-audit/SKILL.md
  - .github/skills/spectra-ingest/SKILL.md
  - LICENSE
  - docs/security/2026-04-06_codex_audit/methodology-and-scope.md
  - .agents/skills/spectra-ingest
  - .agents/skills/spectra-propose
  - pyproject.toml
  - .security-audit/archive/2026-04-06-project-wide-security-audit-2026-04-06/findings/FINDING-002.md
-->

---
### Requirement: OWASP Finding Classification

Each audit finding SHALL include an OWASP-oriented category or CWE-style classification, severity, evidence, impact, and recommended remediation.

#### Scenario: Finding records are actionable

- **WHEN** a reader inspects an individual finding in the initial audit
- **THEN** the finding includes classification, severity, evidence, impact, and recommended remediation


<!-- @trace
source: create-initial-security-audit-baseline
updated: 2026-04-05
code:
  - docs/security/findings/FINDING-002-unauthenticated-student-import.md
  - docs/system-architecture.md
  - .agents/skills/spectra-ask/SKILL.md
  - docs/project-overview.md
  - .agents/skills/spectra-discuss/SKILL.md
  - .agents/skills/spectra-audit/SKILL.md
  - docs/security/initial-audit-report.md
  - docs/security/findings/FINDING-004-overly-permissive-cors.md
  - docs/security/methodology-and-scope.md
  - .agents/skills/spectra-propose/SKILL.md
  - docs/api-and-data-model.md
  - docs/security/findings/FINDING-001-submit-integrity-gap.md
  - docs/security/finding-template.md
  - docs/student-reading-guide.md
  - docs/security/findings/FINDING-003-client-side-token-exposure.md
  - .agents/skills/spectra-debug/SKILL.md
  - docs/backend-frontend-reference.md
  - docs/writing-policy.md
  - docs/operations-and-maintenance.md
  - docs/security/README.md
  - .agents/skills/spectra-apply/SKILL.md
  - docs/README.md
  - .agents/skills/spectra-archive/SKILL.md
  - .agents/skills/spectra-ingest/SKILL.md
  - docs/known-gaps.md
-->

---
### Requirement: Deferred High-Risk Gaps Are Recorded

The initial audit SHALL explicitly record unresolved high-risk gaps, including the unauthenticated `/submit` integrity issue, with status, discussion context, and follow-up ownership instead of omitting them.

#### Scenario: Unresolved high-risk gap remains visible

- **WHEN** the initial audit documents the unauthenticated `/submit` integrity issue
- **THEN** the issue is recorded as an unresolved high-risk finding with status, discussion context, and follow-up ownership


<!-- @trace
source: create-initial-security-audit-baseline
updated: 2026-04-05
code:
  - docs/security/findings/FINDING-002-unauthenticated-student-import.md
  - docs/system-architecture.md
  - .agents/skills/spectra-ask/SKILL.md
  - docs/project-overview.md
  - .agents/skills/spectra-discuss/SKILL.md
  - .agents/skills/spectra-audit/SKILL.md
  - docs/security/initial-audit-report.md
  - docs/security/findings/FINDING-004-overly-permissive-cors.md
  - docs/security/methodology-and-scope.md
  - .agents/skills/spectra-propose/SKILL.md
  - docs/api-and-data-model.md
  - docs/security/findings/FINDING-001-submit-integrity-gap.md
  - docs/security/finding-template.md
  - docs/student-reading-guide.md
  - docs/security/findings/FINDING-003-client-side-token-exposure.md
  - .agents/skills/spectra-debug/SKILL.md
  - docs/backend-frontend-reference.md
  - docs/writing-policy.md
  - docs/operations-and-maintenance.md
  - docs/security/README.md
  - .agents/skills/spectra-apply/SKILL.md
  - docs/README.md
  - .agents/skills/spectra-archive/SKILL.md
  - .agents/skills/spectra-ingest/SKILL.md
  - docs/known-gaps.md
-->

---
### Requirement: Audit Documentation Language Policy

The audit deliverables produced by this change SHALL use Taiwanese Traditional Chinese for prose, SHALL prefer English for technical terms when practical, and SHALL NOT use Mainland China terminology.

#### Scenario: Audit documents follow the language policy

- **WHEN** a reviewer reads files under `docs/security/`, `proposal.md`, `design.md`, or `tasks.md`
- **THEN** the prose uses Taiwanese Traditional Chinese, technical terms remain in English where practical, and Mainland China terminology is absent

<!-- @trace
source: create-initial-security-audit-baseline
updated: 2026-04-05
code:
  - docs/security/findings/FINDING-002-unauthenticated-student-import.md
  - docs/system-architecture.md
  - .agents/skills/spectra-ask/SKILL.md
  - docs/project-overview.md
  - .agents/skills/spectra-discuss/SKILL.md
  - .agents/skills/spectra-audit/SKILL.md
  - docs/security/initial-audit-report.md
  - docs/security/findings/FINDING-004-overly-permissive-cors.md
  - docs/security/methodology-and-scope.md
  - .agents/skills/spectra-propose/SKILL.md
  - docs/api-and-data-model.md
  - docs/security/findings/FINDING-001-submit-integrity-gap.md
  - docs/security/finding-template.md
  - docs/student-reading-guide.md
  - docs/security/findings/FINDING-003-client-side-token-exposure.md
  - .agents/skills/spectra-debug/SKILL.md
  - docs/backend-frontend-reference.md
  - docs/writing-policy.md
  - docs/operations-and-maintenance.md
  - docs/security/README.md
  - .agents/skills/spectra-apply/SKILL.md
  - docs/README.md
  - .agents/skills/spectra-archive/SKILL.md
  - .agents/skills/spectra-ingest/SKILL.md
  - docs/known-gaps.md
-->
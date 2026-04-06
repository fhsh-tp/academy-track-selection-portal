# project-security-audit-lifecycle Specification

## Purpose

TBD - created by archiving change 'refresh-project-security-audit-baseline'. Update Purpose after archive.

## Requirements

### Requirement: Repository-native OWASP audit workspace

The project SHALL store each formal security audit under `.security-audit/` using lifecycle states for `active`, `pending`, and `archive`. Each audit workspace SHALL include status metadata in `.audit.yaml`, and an active audit SHALL include `scope.md`, `plan.md`, and `tasks.md` before review work begins.

#### Scenario: Active audit workspace is initialized

- **WHEN** a maintainer starts a new project-wide security audit
- **THEN** the repository contains `.security-audit/active/<audit-name>/` with `.audit.yaml`, `scope.md`, `plan.md`, and `tasks.md`

#### Scenario: Audit artifacts remain traceable across lifecycle states

- **WHEN** an audit is moved between active, pending, or archive states
- **THEN** the audit name, target repository path, status metadata, and generated artifacts remain grouped under the same audit workspace


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
### Requirement: Audit scope and checklist reflect the current repository state

The project SHALL define each audit's scope, methodology, and review checklist from the current repository state rather than reusing prior conclusions unchanged. The scope SHALL identify included and excluded paths, the current branch or commit under review, the technology stack, trust boundaries, and relevant OWASP review categories. The task checklist SHALL name concrete files or modules for each review category.

#### Scenario: Scope captures the current attack surface

- **WHEN** a maintainer reads an active audit's `scope.md`
- **THEN** the document identifies the current repository path, branch or commit reference, included and excluded boundaries, technology stack, threat model, and primary attack surfaces for the application

#### Scenario: Review tasks are actionable

- **WHEN** a maintainer reads an active audit's `tasks.md`
- **THEN** each task group maps to a review category from `plan.md` and each task names a specific component, file set, or module to inspect

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
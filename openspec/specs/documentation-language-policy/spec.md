# documentation-language-policy Specification

## Purpose

TBD - created by archiving change 'establish-project-documentation-baseline'. Update Purpose after archive.

## Requirements

### Requirement: Documentation Language Policy

All non-spec documentation produced by this change SHALL use Taiwanese Traditional Chinese for prose, SHALL prefer English for technical terms when practical, and SHALL NOT use Mainland China terminology.

#### Scenario: Non-spec documents follow the language policy

- **WHEN** a reviewer reads `proposal.md`, `design.md`, `tasks.md`, or files under `docs/`
- **THEN** the prose uses Taiwanese Traditional Chinese, technical terms remain in English where practical, and Mainland China terminology is absent


<!-- @trace
source: establish-project-documentation-baseline
updated: 2026-04-05
code:
  - .agents/skills/spectra-archive/SKILL.md
  - docs/README.md
  - .agents/skills/spectra-debug/SKILL.md
  - docs/api-and-data-model.md
  - docs/security/methodology-and-scope.md
  - docs/security/initial-audit-report.md
  - docs/writing-policy.md
  - docs/security/finding-template.md
  - docs/project-overview.md
  - .agents/skills/spectra-discuss/SKILL.md
  - docs/system-architecture.md
  - docs/security/findings/FINDING-001-submit-integrity-gap.md
  - docs/security/README.md
  - .agents/skills/spectra-ask/SKILL.md
  - docs/backend-frontend-reference.md
  - .agents/skills/spectra-audit/SKILL.md
  - docs/known-gaps.md
  - .agents/skills/spectra-propose/SKILL.md
  - docs/security/findings/FINDING-004-overly-permissive-cors.md
  - .agents/skills/spectra-ingest/SKILL.md
  - docs/operations-and-maintenance.md
  - docs/security/findings/FINDING-003-client-side-token-exposure.md
  - docs/security/findings/FINDING-002-unauthenticated-student-import.md
  - .agents/skills/spectra-apply/SKILL.md
  - docs/student-reading-guide.md
-->

---
### Requirement: English Normative Specs Exception

Spectra spec files for this change SHALL remain in English normative language while preserving the documentation language policy in proposal, design, tasks, and `docs/` deliverables.

#### Scenario: Spec language follows Spectra conventions

- **WHEN** a reviewer inspects the change spec files under `specs/`
- **THEN** the spec files use English normative language and the non-spec artifacts still follow the documentation language policy

<!-- @trace
source: establish-project-documentation-baseline
updated: 2026-04-05
code:
  - .agents/skills/spectra-archive/SKILL.md
  - docs/README.md
  - .agents/skills/spectra-debug/SKILL.md
  - docs/api-and-data-model.md
  - docs/security/methodology-and-scope.md
  - docs/security/initial-audit-report.md
  - docs/writing-policy.md
  - docs/security/finding-template.md
  - docs/project-overview.md
  - .agents/skills/spectra-discuss/SKILL.md
  - docs/system-architecture.md
  - docs/security/findings/FINDING-001-submit-integrity-gap.md
  - docs/security/README.md
  - .agents/skills/spectra-ask/SKILL.md
  - docs/backend-frontend-reference.md
  - .agents/skills/spectra-audit/SKILL.md
  - docs/known-gaps.md
  - .agents/skills/spectra-propose/SKILL.md
  - docs/security/findings/FINDING-004-overly-permissive-cors.md
  - .agents/skills/spectra-ingest/SKILL.md
  - docs/operations-and-maintenance.md
  - docs/security/findings/FINDING-003-client-side-token-exposure.md
  - docs/security/findings/FINDING-002-unauthenticated-student-import.md
  - .agents/skills/spectra-apply/SKILL.md
  - docs/student-reading-guide.md
-->
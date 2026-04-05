## ADDED Requirements

### Requirement: Initial Security Audit Report

The project SHALL publish an initial security audit under `docs/security/` that defines review scope, methodology, reviewed code areas, findings summary, and remediation priorities.

#### Scenario: Initial audit report is available

- **WHEN** a maintainer opens `docs/security/` after this change
- **THEN** the directory contains an initial audit report with scope, methodology, reviewed areas, findings summary, and remediation priorities

### Requirement: OWASP Finding Classification

Each audit finding SHALL include an OWASP-oriented category or CWE-style classification, severity, evidence, impact, and recommended remediation.

#### Scenario: Finding records are actionable

- **WHEN** a reader inspects an individual finding in the initial audit
- **THEN** the finding includes classification, severity, evidence, impact, and recommended remediation

### Requirement: Deferred High-Risk Gaps Are Recorded

The initial audit SHALL explicitly record unresolved high-risk gaps, including the unauthenticated `/submit` integrity issue, with status, discussion context, and follow-up ownership instead of omitting them.

#### Scenario: Unresolved high-risk gap remains visible

- **WHEN** the initial audit documents the unauthenticated `/submit` integrity issue
- **THEN** the issue is recorded as an unresolved high-risk finding with status, discussion context, and follow-up ownership

### Requirement: Audit Documentation Language Policy

The audit deliverables produced by this change SHALL use Taiwanese Traditional Chinese for prose, SHALL prefer English for technical terms when practical, and SHALL NOT use Mainland China terminology.

#### Scenario: Audit documents follow the language policy

- **WHEN** a reviewer reads files under `docs/security/`, `proposal.md`, `design.md`, or `tasks.md`
- **THEN** the prose uses Taiwanese Traditional Chinese, technical terms remain in English where practical, and Mainland China terminology is absent

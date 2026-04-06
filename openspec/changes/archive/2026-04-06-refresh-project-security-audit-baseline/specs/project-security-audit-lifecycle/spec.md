## ADDED Requirements

### Requirement: Repository-native OWASP audit workspace

The project SHALL store each formal security audit under `.security-audit/` using lifecycle states for `active`, `pending`, and `archive`. Each audit workspace SHALL include status metadata in `.audit.yaml`, and an active audit SHALL include `scope.md`, `plan.md`, and `tasks.md` before review work begins.

#### Scenario: Active audit workspace is initialized

- **WHEN** a maintainer starts a new project-wide security audit
- **THEN** the repository contains `.security-audit/active/<audit-name>/` with `.audit.yaml`, `scope.md`, `plan.md`, and `tasks.md`

#### Scenario: Audit artifacts remain traceable across lifecycle states

- **WHEN** an audit is moved between active, pending, or archive states
- **THEN** the audit name, target repository path, status metadata, and generated artifacts remain grouped under the same audit workspace

### Requirement: Audit scope and checklist reflect the current repository state

The project SHALL define each audit's scope, methodology, and review checklist from the current repository state rather than reusing prior conclusions unchanged. The scope SHALL identify included and excluded paths, the current branch or commit under review, the technology stack, trust boundaries, and relevant OWASP review categories. The task checklist SHALL name concrete files or modules for each review category.

#### Scenario: Scope captures the current attack surface

- **WHEN** a maintainer reads an active audit's `scope.md`
- **THEN** the document identifies the current repository path, branch or commit reference, included and excluded boundaries, technology stack, threat model, and primary attack surfaces for the application

#### Scenario: Review tasks are actionable

- **WHEN** a maintainer reads an active audit's `tasks.md`
- **THEN** each task group maps to a review category from `plan.md` and each task names a specific component, file set, or module to inspect

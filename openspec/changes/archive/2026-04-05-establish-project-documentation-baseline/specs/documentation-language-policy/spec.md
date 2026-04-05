## ADDED Requirements

### Requirement: Documentation Language Policy

All non-spec documentation produced by this change SHALL use Taiwanese Traditional Chinese for prose, SHALL prefer English for technical terms when practical, and SHALL NOT use Mainland China terminology.

#### Scenario: Non-spec documents follow the language policy

- **WHEN** a reviewer reads `proposal.md`, `design.md`, `tasks.md`, or files under `docs/`
- **THEN** the prose uses Taiwanese Traditional Chinese, technical terms remain in English where practical, and Mainland China terminology is absent

### Requirement: English Normative Specs Exception

Spectra spec files for this change SHALL remain in English normative language while preserving the documentation language policy in proposal, design, tasks, and `docs/` deliverables.

#### Scenario: Spec language follows Spectra conventions

- **WHEN** a reviewer inspects the change spec files under `specs/`
- **THEN** the spec files use English normative language and the non-spec artifacts still follow the documentation language policy

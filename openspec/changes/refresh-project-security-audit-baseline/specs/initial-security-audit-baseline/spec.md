## MODIFIED Requirements

### Requirement: Initial Security Audit Report

The project SHALL publish a current security audit baseline under `docs/security/` that identifies the reviewed audit name, review date, branch or commit reference, scope, methodology, reviewed code areas, findings summary, remediation priorities, and references to the supporting OWASP audit artifacts used to produce the baseline.

#### Scenario: Current audit baseline is available

- **WHEN** a maintainer opens `docs/security/` after this change
- **THEN** the directory contains a current security audit baseline with the reviewed audit name, review date, branch or commit reference, scope, methodology, reviewed areas, findings summary, and remediation priorities

#### Scenario: Published baseline is traceable to supporting audit artifacts

- **WHEN** a maintainer follows the references from the published security audit baseline
- **THEN** the baseline identifies the supporting OWASP audit workspace and the related scope, plan, findings, or report artifacts for that review

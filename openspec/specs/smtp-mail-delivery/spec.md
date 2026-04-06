# smtp-mail-delivery Specification

## Purpose

TBD - created by archiving change 'dockerize-with-uv-smtp-relay'. Update Purpose after archive.

## Requirements

### Requirement: SMTP Relay Connection

The mailer module SHALL connect to Google Workspace SMTP Relay at the host specified by `SMTP_HOST` (default: `smtp-relay.gmail.com`) on the port specified by `SMTP_PORT` (default: `587`) using STARTTLS encryption. The connection SHALL authenticate with `SMTP_USER` and `SMTP_PASSWORD`. The mailer SHALL NOT fall back to unencrypted connections.

#### Scenario: Successful SMTP connection

- **WHEN** `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, and `SMTP_PASSWORD` are all set and valid
- **THEN** the mailer establishes a STARTTLS-encrypted connection to the SMTP server and authenticates successfully

#### Scenario: Missing credentials

- **WHEN** `SMTP_USER` or `SMTP_PASSWORD` is not set
- **THEN** the mailer logs an error and returns `False` without attempting a connection


<!-- @trace
source: dockerize-with-uv-smtp-relay
updated: 2026-04-06
code:
  - .agents/skills/spectra-audit
  - .agents/skills/spectra-propose
  - backend/static/TW-Kai-98_1.ttf
  - docs/security/2026-04-05_codex_audit/initial-audit-report.md
  - .github/skills/spectra-ask/SKILL.md
  - .security-audit/archive/2026-04-06-project-wide-security-audit-2026-04-06/tasks.md
  - docs/security/2026-04-06_codex_audit/dependency-vulnerability-scan.md
  - nginx/nginx.conf
  - backend/security.py
  - .github/prompts/spectra-ask.prompt.md
  - docs/security/methodology-and-scope.md
  - .security-audit/archive/2026-04-06-project-wide-security-audit-2026-04-06/findings/FINDING-003.md
  - scripts/buildx.sh
  - nginx/entrypoint.sh
  - docs/security/2026-04-05_codex_audit/finding-template.md
  - .github/prompts/spectra-archive.prompt.md
  - .agents/skills/spectra-debug/SKILL.md
  - docs/security/2026-04-05_codex_audit/findings/FINDING-001-submit-integrity-gap.md
  - .security-audit/archive/2026-04-06-project-wide-security-audit-2026-04-06/findings/FINDING-001.md
  - docs/security/2026-04-06_codex_audit/initial-audit-report.md
  - .agents/skills/spectra-apply/SKILL.md
  - .agents/skills/spectra-ask
  - docs/security/2026-04-05_codex_audit/findings/FINDING-003-client-side-token-exposure.md
  - docs/security/README.md
  - .github/prompts/spectra-propose.prompt.md
  - .security-audit/archive/2026-04-06-project-wide-security-audit-2026-04-06/findings/FINDING-004.md
  - docs/security/finding-template.md
  - frontend/style.css
  - .agents/skills/spectra-ingest
  - .security-audit/archive/2026-04-06-project-wide-security-audit-2026-04-06/report-tw.md
  - .github/prompts/spectra-apply.prompt.md
  - .github/skills/spectra-propose/SKILL.md
  - backend/mailer.py
  - backend/utils/__init__.py
  - frontend/config.js
  - docs/security/findings/FINDING-002-unauthenticated-student-import.md
  - .github/skills/spectra-archive/SKILL.md
  - .agents/skills/spectra-debug
  - .github/skills/spectra-apply/SKILL.md
  - .github/prompts/spectra-debug.prompt.md
  - requirements.txt
  - docs/security/2026-04-06_codex_audit/README.md
  - scripts/docker-entrypoint.sh
  - .env.example
  - .github/skills/spectra-debug/SKILL.md
  - backend/utils/dependencies.py
  - .github/prompts/spectra-audit.prompt.md
  - docs/security/initial-audit-report.md
  - .github/prompts/spectra-discuss.prompt.md
  - backend/main.py
  - .github/skills/spectra-audit/SKILL.md
  - docs/security/2026-04-05_codex_audit/findings/FINDING-002-unauthenticated-student-import.md
  - backend/database.py
  - backend/utils/email.py
  - .github/skills/spectra-discuss/SKILL.md
  - docs/security/findings/FINDING-001-submit-integrity-gap.md
  - .agents/skills/spectra-archive
  - frontend/admin.html
  - .github/skills/spectra-ingest/SKILL.md
  - frontend/static/config.js
  - .agents/skills/spectra-discuss/SKILL.md
  - docker-compose.yml
  - backend/static/TW-Kai-Ext-B-98_1.ttf
  - .github/prompts/spectra-ingest.prompt.md
  - docs/security/2026-04-05_codex_audit/findings/FINDING-004-overly-permissive-cors.md
  - LICENSE
  - frontend/static/style.css
  - pyproject.toml
  - .security-audit/archive/2026-04-06-project-wide-security-audit-2026-04-06/findings/FINDING-002.md
  - .agents/skills/spectra-propose/SKILL.md
  - .agents/skills/spectra-archive/SKILL.md
  - .security-audit/archive/2026-04-06-project-wide-security-audit-2026-04-06/.audit.yaml
  - .agents/skills/spectra-discuss
  - uv.lock
  - .agents/skills/spectra-audit/SKILL.md
  - .agents/skills/spectra-ingest/SKILL.md
  - .agents/skills/spectra-ask/SKILL.md
  - .security-audit/archive/2026-04-06-project-wide-security-audit-2026-04-06/report-en.md
  - .security-audit/archive/2026-04-06-project-wide-security-audit-2026-04-06/scope.md
  - nginx/Dockerfile
  - README.md
  - docs/security/2026-04-05_codex_audit/methodology-and-scope.md
  - Dockerfile
  - .security-audit/archive/2026-04-06-project-wide-security-audit-2026-04-06/plan.md
  - .spectra.yaml
  - docs/security/2026-04-06_codex_audit/methodology-and-scope.md
  - docs/security/2026-04-05_codex_audit/README.md
  - docs/security/findings/FINDING-004-overly-permissive-cors.md
  - frontend/index.html
  - .agents/skills/spectra-apply
  - docs/security/findings/FINDING-003-client-side-token-exposure.md
-->

---
### Requirement: Async Email Sending

The `send_confirmation_email` function SHALL be an `async def` coroutine using `aiosmtplib`. It SHALL NOT use `asyncio.to_thread` or any blocking SMTP library. Email sending SHALL not block the FastAPI event loop.

#### Scenario: Email sent without blocking

- **WHEN** `POST /submit` is called and triggers email sending
- **THEN** the email is sent asynchronously and the API response is returned without waiting for the SMTP connection to complete (email is awaited before response is returned, but does not block other requests)


<!-- @trace
source: dockerize-with-uv-smtp-relay
updated: 2026-04-06
code:
  - .agents/skills/spectra-audit
  - .agents/skills/spectra-propose
  - backend/static/TW-Kai-98_1.ttf
  - docs/security/2026-04-05_codex_audit/initial-audit-report.md
  - .github/skills/spectra-ask/SKILL.md
  - .security-audit/archive/2026-04-06-project-wide-security-audit-2026-04-06/tasks.md
  - docs/security/2026-04-06_codex_audit/dependency-vulnerability-scan.md
  - nginx/nginx.conf
  - backend/security.py
  - .github/prompts/spectra-ask.prompt.md
  - docs/security/methodology-and-scope.md
  - .security-audit/archive/2026-04-06-project-wide-security-audit-2026-04-06/findings/FINDING-003.md
  - scripts/buildx.sh
  - nginx/entrypoint.sh
  - docs/security/2026-04-05_codex_audit/finding-template.md
  - .github/prompts/spectra-archive.prompt.md
  - .agents/skills/spectra-debug/SKILL.md
  - docs/security/2026-04-05_codex_audit/findings/FINDING-001-submit-integrity-gap.md
  - .security-audit/archive/2026-04-06-project-wide-security-audit-2026-04-06/findings/FINDING-001.md
  - docs/security/2026-04-06_codex_audit/initial-audit-report.md
  - .agents/skills/spectra-apply/SKILL.md
  - .agents/skills/spectra-ask
  - docs/security/2026-04-05_codex_audit/findings/FINDING-003-client-side-token-exposure.md
  - docs/security/README.md
  - .github/prompts/spectra-propose.prompt.md
  - .security-audit/archive/2026-04-06-project-wide-security-audit-2026-04-06/findings/FINDING-004.md
  - docs/security/finding-template.md
  - frontend/style.css
  - .agents/skills/spectra-ingest
  - .security-audit/archive/2026-04-06-project-wide-security-audit-2026-04-06/report-tw.md
  - .github/prompts/spectra-apply.prompt.md
  - .github/skills/spectra-propose/SKILL.md
  - backend/mailer.py
  - backend/utils/__init__.py
  - frontend/config.js
  - docs/security/findings/FINDING-002-unauthenticated-student-import.md
  - .github/skills/spectra-archive/SKILL.md
  - .agents/skills/spectra-debug
  - .github/skills/spectra-apply/SKILL.md
  - .github/prompts/spectra-debug.prompt.md
  - requirements.txt
  - docs/security/2026-04-06_codex_audit/README.md
  - scripts/docker-entrypoint.sh
  - .env.example
  - .github/skills/spectra-debug/SKILL.md
  - backend/utils/dependencies.py
  - .github/prompts/spectra-audit.prompt.md
  - docs/security/initial-audit-report.md
  - .github/prompts/spectra-discuss.prompt.md
  - backend/main.py
  - .github/skills/spectra-audit/SKILL.md
  - docs/security/2026-04-05_codex_audit/findings/FINDING-002-unauthenticated-student-import.md
  - backend/database.py
  - backend/utils/email.py
  - .github/skills/spectra-discuss/SKILL.md
  - docs/security/findings/FINDING-001-submit-integrity-gap.md
  - .agents/skills/spectra-archive
  - frontend/admin.html
  - .github/skills/spectra-ingest/SKILL.md
  - frontend/static/config.js
  - .agents/skills/spectra-discuss/SKILL.md
  - docker-compose.yml
  - backend/static/TW-Kai-Ext-B-98_1.ttf
  - .github/prompts/spectra-ingest.prompt.md
  - docs/security/2026-04-05_codex_audit/findings/FINDING-004-overly-permissive-cors.md
  - LICENSE
  - frontend/static/style.css
  - pyproject.toml
  - .security-audit/archive/2026-04-06-project-wide-security-audit-2026-04-06/findings/FINDING-002.md
  - .agents/skills/spectra-propose/SKILL.md
  - .agents/skills/spectra-archive/SKILL.md
  - .security-audit/archive/2026-04-06-project-wide-security-audit-2026-04-06/.audit.yaml
  - .agents/skills/spectra-discuss
  - uv.lock
  - .agents/skills/spectra-audit/SKILL.md
  - .agents/skills/spectra-ingest/SKILL.md
  - .agents/skills/spectra-ask/SKILL.md
  - .security-audit/archive/2026-04-06-project-wide-security-audit-2026-04-06/report-en.md
  - .security-audit/archive/2026-04-06-project-wide-security-audit-2026-04-06/scope.md
  - nginx/Dockerfile
  - README.md
  - docs/security/2026-04-05_codex_audit/methodology-and-scope.md
  - Dockerfile
  - .security-audit/archive/2026-04-06-project-wide-security-audit-2026-04-06/plan.md
  - .spectra.yaml
  - docs/security/2026-04-06_codex_audit/methodology-and-scope.md
  - docs/security/2026-04-05_codex_audit/README.md
  - docs/security/findings/FINDING-004-overly-permissive-cors.md
  - frontend/index.html
  - .agents/skills/spectra-apply
  - docs/security/findings/FINDING-003-client-side-token-exposure.md
-->

---
### Requirement: Selection Confirmation Email

When a student successfully submits their track selection, the system SHALL send a confirmation email to the student's registered email address. The email SHALL include: student name, student ID, class number, selected track name, submission timestamp (converted to Asia/Taipei timezone), and a PDF attachment (`<student_id>_確認書.pdf`) containing the formal selection form.

#### Scenario: Confirmation email with PDF

- **WHEN** a student submits a valid track selection and `pdf_bytes` is non-empty
- **THEN** an email with subject `【重要確認信】<name> 的選填結果` is sent to the student's email with the PDF attached

#### Scenario: PDF generation failure

- **WHEN** `generate_formal_pdf` returns empty bytes or `None`
- **THEN** the API returns `{"status": "error", "message": "PDF 生成失敗"}` and no email is sent


<!-- @trace
source: dockerize-with-uv-smtp-relay
updated: 2026-04-06
code:
  - .agents/skills/spectra-audit
  - .agents/skills/spectra-propose
  - backend/static/TW-Kai-98_1.ttf
  - docs/security/2026-04-05_codex_audit/initial-audit-report.md
  - .github/skills/spectra-ask/SKILL.md
  - .security-audit/archive/2026-04-06-project-wide-security-audit-2026-04-06/tasks.md
  - docs/security/2026-04-06_codex_audit/dependency-vulnerability-scan.md
  - nginx/nginx.conf
  - backend/security.py
  - .github/prompts/spectra-ask.prompt.md
  - docs/security/methodology-and-scope.md
  - .security-audit/archive/2026-04-06-project-wide-security-audit-2026-04-06/findings/FINDING-003.md
  - scripts/buildx.sh
  - nginx/entrypoint.sh
  - docs/security/2026-04-05_codex_audit/finding-template.md
  - .github/prompts/spectra-archive.prompt.md
  - .agents/skills/spectra-debug/SKILL.md
  - docs/security/2026-04-05_codex_audit/findings/FINDING-001-submit-integrity-gap.md
  - .security-audit/archive/2026-04-06-project-wide-security-audit-2026-04-06/findings/FINDING-001.md
  - docs/security/2026-04-06_codex_audit/initial-audit-report.md
  - .agents/skills/spectra-apply/SKILL.md
  - .agents/skills/spectra-ask
  - docs/security/2026-04-05_codex_audit/findings/FINDING-003-client-side-token-exposure.md
  - docs/security/README.md
  - .github/prompts/spectra-propose.prompt.md
  - .security-audit/archive/2026-04-06-project-wide-security-audit-2026-04-06/findings/FINDING-004.md
  - docs/security/finding-template.md
  - frontend/style.css
  - .agents/skills/spectra-ingest
  - .security-audit/archive/2026-04-06-project-wide-security-audit-2026-04-06/report-tw.md
  - .github/prompts/spectra-apply.prompt.md
  - .github/skills/spectra-propose/SKILL.md
  - backend/mailer.py
  - backend/utils/__init__.py
  - frontend/config.js
  - docs/security/findings/FINDING-002-unauthenticated-student-import.md
  - .github/skills/spectra-archive/SKILL.md
  - .agents/skills/spectra-debug
  - .github/skills/spectra-apply/SKILL.md
  - .github/prompts/spectra-debug.prompt.md
  - requirements.txt
  - docs/security/2026-04-06_codex_audit/README.md
  - scripts/docker-entrypoint.sh
  - .env.example
  - .github/skills/spectra-debug/SKILL.md
  - backend/utils/dependencies.py
  - .github/prompts/spectra-audit.prompt.md
  - docs/security/initial-audit-report.md
  - .github/prompts/spectra-discuss.prompt.md
  - backend/main.py
  - .github/skills/spectra-audit/SKILL.md
  - docs/security/2026-04-05_codex_audit/findings/FINDING-002-unauthenticated-student-import.md
  - backend/database.py
  - backend/utils/email.py
  - .github/skills/spectra-discuss/SKILL.md
  - docs/security/findings/FINDING-001-submit-integrity-gap.md
  - .agents/skills/spectra-archive
  - frontend/admin.html
  - .github/skills/spectra-ingest/SKILL.md
  - frontend/static/config.js
  - .agents/skills/spectra-discuss/SKILL.md
  - docker-compose.yml
  - backend/static/TW-Kai-Ext-B-98_1.ttf
  - .github/prompts/spectra-ingest.prompt.md
  - docs/security/2026-04-05_codex_audit/findings/FINDING-004-overly-permissive-cors.md
  - LICENSE
  - frontend/static/style.css
  - pyproject.toml
  - .security-audit/archive/2026-04-06-project-wide-security-audit-2026-04-06/findings/FINDING-002.md
  - .agents/skills/spectra-propose/SKILL.md
  - .agents/skills/spectra-archive/SKILL.md
  - .security-audit/archive/2026-04-06-project-wide-security-audit-2026-04-06/.audit.yaml
  - .agents/skills/spectra-discuss
  - uv.lock
  - .agents/skills/spectra-audit/SKILL.md
  - .agents/skills/spectra-ingest/SKILL.md
  - .agents/skills/spectra-ask/SKILL.md
  - .security-audit/archive/2026-04-06-project-wide-security-audit-2026-04-06/report-en.md
  - .security-audit/archive/2026-04-06-project-wide-security-audit-2026-04-06/scope.md
  - nginx/Dockerfile
  - README.md
  - docs/security/2026-04-05_codex_audit/methodology-and-scope.md
  - Dockerfile
  - .security-audit/archive/2026-04-06-project-wide-security-audit-2026-04-06/plan.md
  - .spectra.yaml
  - docs/security/2026-04-06_codex_audit/methodology-and-scope.md
  - docs/security/2026-04-05_codex_audit/README.md
  - docs/security/findings/FINDING-004-overly-permissive-cors.md
  - frontend/index.html
  - .agents/skills/spectra-apply
  - docs/security/findings/FINDING-003-client-side-token-exposure.md
-->

---
### Requirement: Reminder Email

When an admin triggers the reminder function, the system SHALL send a reminder email to each student who has not yet submitted a track selection and has a registered email address. Reminder emails SHALL NOT include a PDF attachment. The system SHALL wait at least 1 second between each email send to avoid triggering SMTP rate limiting.

#### Scenario: Reminder sent to unsubmitted student

- **WHEN** admin calls `POST /admin/send-reminders` and a student has no entry in the `selections` table
- **THEN** an email with subject `【重要通知】您的類組尚未選填` is sent to that student

#### Scenario: No reminder sent to completed students

- **WHEN** a student already has a `selections` record
- **THEN** that student SHALL NOT receive a reminder email

#### Scenario: Rate limiting delay

- **WHEN** sending reminder emails to multiple students
- **THEN** the system SHALL pause at least 1 second between each email send

<!-- @trace
source: dockerize-with-uv-smtp-relay
updated: 2026-04-06
code:
  - .agents/skills/spectra-audit
  - .agents/skills/spectra-propose
  - backend/static/TW-Kai-98_1.ttf
  - docs/security/2026-04-05_codex_audit/initial-audit-report.md
  - .github/skills/spectra-ask/SKILL.md
  - .security-audit/archive/2026-04-06-project-wide-security-audit-2026-04-06/tasks.md
  - docs/security/2026-04-06_codex_audit/dependency-vulnerability-scan.md
  - nginx/nginx.conf
  - backend/security.py
  - .github/prompts/spectra-ask.prompt.md
  - docs/security/methodology-and-scope.md
  - .security-audit/archive/2026-04-06-project-wide-security-audit-2026-04-06/findings/FINDING-003.md
  - scripts/buildx.sh
  - nginx/entrypoint.sh
  - docs/security/2026-04-05_codex_audit/finding-template.md
  - .github/prompts/spectra-archive.prompt.md
  - .agents/skills/spectra-debug/SKILL.md
  - docs/security/2026-04-05_codex_audit/findings/FINDING-001-submit-integrity-gap.md
  - .security-audit/archive/2026-04-06-project-wide-security-audit-2026-04-06/findings/FINDING-001.md
  - docs/security/2026-04-06_codex_audit/initial-audit-report.md
  - .agents/skills/spectra-apply/SKILL.md
  - .agents/skills/spectra-ask
  - docs/security/2026-04-05_codex_audit/findings/FINDING-003-client-side-token-exposure.md
  - docs/security/README.md
  - .github/prompts/spectra-propose.prompt.md
  - .security-audit/archive/2026-04-06-project-wide-security-audit-2026-04-06/findings/FINDING-004.md
  - docs/security/finding-template.md
  - frontend/style.css
  - .agents/skills/spectra-ingest
  - .security-audit/archive/2026-04-06-project-wide-security-audit-2026-04-06/report-tw.md
  - .github/prompts/spectra-apply.prompt.md
  - .github/skills/spectra-propose/SKILL.md
  - backend/mailer.py
  - backend/utils/__init__.py
  - frontend/config.js
  - docs/security/findings/FINDING-002-unauthenticated-student-import.md
  - .github/skills/spectra-archive/SKILL.md
  - .agents/skills/spectra-debug
  - .github/skills/spectra-apply/SKILL.md
  - .github/prompts/spectra-debug.prompt.md
  - requirements.txt
  - docs/security/2026-04-06_codex_audit/README.md
  - scripts/docker-entrypoint.sh
  - .env.example
  - .github/skills/spectra-debug/SKILL.md
  - backend/utils/dependencies.py
  - .github/prompts/spectra-audit.prompt.md
  - docs/security/initial-audit-report.md
  - .github/prompts/spectra-discuss.prompt.md
  - backend/main.py
  - .github/skills/spectra-audit/SKILL.md
  - docs/security/2026-04-05_codex_audit/findings/FINDING-002-unauthenticated-student-import.md
  - backend/database.py
  - backend/utils/email.py
  - .github/skills/spectra-discuss/SKILL.md
  - docs/security/findings/FINDING-001-submit-integrity-gap.md
  - .agents/skills/spectra-archive
  - frontend/admin.html
  - .github/skills/spectra-ingest/SKILL.md
  - frontend/static/config.js
  - .agents/skills/spectra-discuss/SKILL.md
  - docker-compose.yml
  - backend/static/TW-Kai-Ext-B-98_1.ttf
  - .github/prompts/spectra-ingest.prompt.md
  - docs/security/2026-04-05_codex_audit/findings/FINDING-004-overly-permissive-cors.md
  - LICENSE
  - frontend/static/style.css
  - pyproject.toml
  - .security-audit/archive/2026-04-06-project-wide-security-audit-2026-04-06/findings/FINDING-002.md
  - .agents/skills/spectra-propose/SKILL.md
  - .agents/skills/spectra-archive/SKILL.md
  - .security-audit/archive/2026-04-06-project-wide-security-audit-2026-04-06/.audit.yaml
  - .agents/skills/spectra-discuss
  - uv.lock
  - .agents/skills/spectra-audit/SKILL.md
  - .agents/skills/spectra-ingest/SKILL.md
  - .agents/skills/spectra-ask/SKILL.md
  - .security-audit/archive/2026-04-06-project-wide-security-audit-2026-04-06/report-en.md
  - .security-audit/archive/2026-04-06-project-wide-security-audit-2026-04-06/scope.md
  - nginx/Dockerfile
  - README.md
  - docs/security/2026-04-05_codex_audit/methodology-and-scope.md
  - Dockerfile
  - .security-audit/archive/2026-04-06-project-wide-security-audit-2026-04-06/plan.md
  - .spectra.yaml
  - docs/security/2026-04-06_codex_audit/methodology-and-scope.md
  - docs/security/2026-04-05_codex_audit/README.md
  - docs/security/findings/FINDING-004-overly-permissive-cors.md
  - frontend/index.html
  - .agents/skills/spectra-apply
  - docs/security/findings/FINDING-003-client-side-token-exposure.md
-->
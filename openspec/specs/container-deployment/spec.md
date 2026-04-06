# container-deployment Specification

## Purpose

TBD - created by archiving change 'dockerize-with-uv-smtp-relay'. Update Purpose after archive.

## Requirements

### Requirement: Docker Compose Service Topology

The system SHALL be fully deployable using `docker compose up --build -d` with four services: `db` (PostgreSQL), `backend` (FastAPI + Gunicorn), `nginx` (static files + API proxy), and `cloudflared` (Cloudflare Tunnel). All services SHALL communicate over a shared Docker internal network. The `backend` service SHALL depend on `db`, and `nginx` SHALL depend on `backend`, and `cloudflared` SHALL depend on `nginx`.

#### Scenario: Full stack starts successfully

- **WHEN** operator runs `docker compose up --build -d` with a valid `.env` file
- **THEN** all four services reach a running state, the application is accessible through the Cloudflare Tunnel URL, and the database is initialized with the admin user

#### Scenario: Backend waits for database

- **WHEN** `db` service is slow to start
- **THEN** `backend` service SHALL retry the database connection and not crash before `db` is ready


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
### Requirement: Python Dependency Management via uv

The system SHALL use `pyproject.toml` and `uv.lock` to declare and lock all Python dependencies. The `Dockerfile` for the backend SHALL install dependencies using `uv sync --frozen --no-dev`, ensuring bit-for-bit reproducible builds. `requirements.txt` SHALL be removed.

#### Scenario: Reproducible backend build

- **WHEN** the backend Docker image is built on any machine with the same `uv.lock`
- **THEN** the installed packages SHALL be identical to those on any other machine building from the same lock file

#### Scenario: Adding a new dependency

- **WHEN** a developer runs `uv add <package>`
- **THEN** `pyproject.toml` and `uv.lock` are updated, and the next `docker compose build` installs the new package


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
### Requirement: nginx Static File Serving

The `nginx` service SHALL serve all files in the `frontend/` directory as static assets. nginx SHALL map the following URL paths to their corresponding HTML files without requiring the `.html` extension: `/` → `index.html`, `/login` → `login.html`, `/choose` → `choose.html`, `/admin` → `admin.html`, `/admin-login` → `admin-login.html`.

#### Scenario: Student accesses login page

- **WHEN** a browser requests `GET /login`
- **THEN** nginx returns `login.html` with status 200

#### Scenario: Font file request

- **WHEN** a browser requests `/TW-Kai-98_1.ttf`
- **THEN** nginx returns the font file with the correct MIME type


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
### Requirement: nginx API Proxy

The `nginx` service SHALL proxy the following routes to `http://backend:8000`, preserving the original request method and body: `POST /login`, `POST /admin-login`, `POST /submit`, `GET /admin/all`, `POST /admin/import-students`, `POST /admin/send-reminders`. All other routes SHALL be handled as static files.

#### Scenario: Login API proxied correctly

- **WHEN** a browser sends `POST /login` with JSON credentials
- **THEN** nginx proxies the request to `backend:8000/login` and returns the backend response to the browser

#### Scenario: Static file takes precedence over proxy

- **WHEN** a browser sends `GET /choose`
- **THEN** nginx serves `choose.html` directly without contacting the backend


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
### Requirement: Frontend API URL Injection

The `frontend/config.js` file SHALL contain the placeholder string `__API_BASE_URL__` in place of any hardcoded URL. The nginx container's `entrypoint.sh` SHALL replace `__API_BASE_URL__` with the value of the `API_BASE_URL` environment variable at container startup using `sed`. When `API_BASE_URL` is empty (default), the frontend SHALL use relative paths.

#### Scenario: Production URL injection

- **WHEN** the nginx container starts with `API_BASE_URL=https://portal.school.edu.tw`
- **THEN** `config.js` at runtime contains `API_BASE_URL: "https://portal.school.edu.tw"`

#### Scenario: Default relative path

- **WHEN** the nginx container starts with `API_BASE_URL` unset or empty
- **THEN** `config.js` at runtime contains `API_BASE_URL: ""`, and all API calls use relative paths


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
### Requirement: Environment Variable Configuration

All runtime configuration SHALL be sourced from environment variables. A `.env.example` file SHALL document every required and optional environment variable with description and safe default values. The `docker-compose.yml` SHALL provide default values for non-secret variables (e.g., `SMTP_HOST`, `SMTP_PORT`, `DB_SSLMODE`, `TUNNEL_TRANSPORT_PROTOCOL`) so that the service starts with minimal `.env` configuration.

#### Scenario: Minimal .env for local development

- **WHEN** an operator creates a `.env` with only `SECRET_KEY`, `ADMIN_PASSWORD`, `SMTP_USER`, `SMTP_PASSWORD`, and `TUNNEL_TOKEN`
- **THEN** all services start and function correctly using Docker Compose default values for all other variables

#### Scenario: DB SSL mode override

- **WHEN** `DB_SSLMODE=require` is set in the environment
- **THEN** the backend connects to PostgreSQL with SSL required, and the connection fails if SSL is not available


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
### Requirement: Cloudflare Tunnel Integration

The `cloudflared` service SHALL authenticate with Cloudflare using the `TUNNEL_TOKEN` environment variable and run with `tunnel run --no-autoupdate`. The transport protocol SHALL be configurable via `TUNNEL_TRANSPORT_PROTOCOL` (values: `auto`, `quic`, `http2`; default: `auto`). The tunnel SHALL route incoming traffic to `http://nginx:80`.

#### Scenario: Tunnel connects on startup

- **WHEN** `cloudflared` starts with a valid `TUNNEL_TOKEN`
- **THEN** the service connects to Cloudflare and the configured public hostname resolves to the application

#### Scenario: Protocol fallback

- **WHEN** `TUNNEL_TRANSPORT_PROTOCOL=auto` and UDP is blocked on the network
- **THEN** cloudflared falls back to HTTP/2 over TCP and the tunnel remains operational

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
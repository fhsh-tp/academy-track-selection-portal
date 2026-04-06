# Security Audit Report

## Executive Summary

A source-code security audit of **academy-track-selection-portal** was conducted on **2026-04-06** against branch **`refactor/security-enhance`** at commit **`c72ebdda6aefc64a59a9a2234d1babc158bcc6c5`**. The review covered the FastAPI backend, static frontend, authentication and authorization flows, CSV import paths, email delivery logic, deployment configuration, and locked Python dependencies. A total of **4** active findings were identified: **0 Critical**, **1 High**, **3 Medium**, and **0 Low**.

Overall risk is **elevated but narrower than the 2026-04-05 baseline**. Three previously reported issues were no longer reproducible in the current codebase: the unauthenticated `/submit` write path, the unauthenticated student import route, and the wildcard CORS configuration. The remaining highest-risk concerns are a deployable default admin password path, browser-readable JWT storage combined with permissive script execution, missing authentication throttling, and verbose backend error disclosure in the import workflow. Positive observations include parameterized SQL usage on reviewed routes and a clean locked dependency scan with **no known vulnerabilities found** at audit time.

## Audit Scope

### 2.1 Target

| Item | Details |
|---|---|
| Application Name | academy-track-selection-portal |
| Version / Commit | `refactor/security-enhance` / `c72ebdda6aefc64a59a9a2234d1babc158bcc6c5` |
| Repository | `/Users/phoenix/dev/fhsh-projects/academy-track-selection-portal` |
| Environment | Repository static review |
| Date Range | 2026-04-06 to 2026-04-06 |
| Audit Name | `project-wide-security-audit-2026-04-06` |

### 2.2 Boundaries

**In-Scope:**

- `backend/main.py`, `backend/security.py`, `backend/database.py`, `backend/mailer.py`, `backend/utils/email.py`
- `frontend/login.html`, `frontend/admin-login.html`, `frontend/choose.html`, `frontend/admin.html`, `frontend/index.html`, `frontend/static/config.js`
- `nginx/nginx.conf`, `nginx/entrypoint.sh`, `Dockerfile`, `docker-compose.yml`, `scripts/docker-entrypoint.sh`
- `import_students.py`, `pyproject.toml`, `uv.lock`, `.env.example`
- Historical comparison against `docs/security/2026-04-05_codex_audit/`

**Out-of-Scope:**

- Runtime exploitation or dynamic penetration testing
- Deployment-console settings for Cloudflare, SMTP provider, or host OS
- Real `.env` secret values
- Binary font assets and non-security CSS styling

### 2.3 Technology Stack

| Layer | Technology |
|---|---|
| Language | Python 3.12+, HTML, JavaScript |
| Framework | FastAPI, Pydantic, Nginx |
| Database | PostgreSQL via `psycopg2` |
| Authentication | JWT (`python-jose`), bearer token flow, `bcrypt` |
| Email / PDF | `aiosmtplib`, ReportLab |
| Packaging | `uv`, `pyproject.toml`, `uv.lock` |
| Deployment | Docker, Docker Compose, Cloudflare Tunnel |

### 2.4 Standards Applied

- OWASP Top 10 (2021)
- OWASP Web Security Testing Guide v4.2
- OWASP Code Review Guide v2
- CWE/SANS Top 25

## Methodology

The audit used a hybrid manual-review workflow centered on OWASP category-based source inspection. Review categories covered authentication, authorization, session management, input validation, injection, cryptography, error handling, logging and monitoring, data protection, and dependency / supply-chain risk. Findings were verified by tracing user-controlled inputs across the current code paths and recording file-level evidence.

### 3.1 Legacy Baseline Re-verification

The 2026-04-05 baseline was treated as historical input, not as current truth. Re-verification produced these outcomes:

- Prior `FINDING-001` (unauthenticated `/submit`) is **closed** in the current code because `/submit` now requires `Depends(get_current_user)` and enforces `student_id` to token identity binding in `backend/main.py:130-137`.
- Prior `FINDING-002` (unauthenticated student import) is **closed** in the current code because `/admin/import-students` now requires authentication and `role == admin` in `backend/main.py:213-216`.
- Prior `FINDING-003` (client-side token exposure) is **retained and rewritten** as current `FINDING-002`.
- Prior `FINDING-004` (wildcard CORS) is **closed** because origins are now derived from an allow-list in `backend/main.py:44-55` rather than `["*"]`.

### 3.2 Dependency Vulnerability Scan

A locked dependency scan was executed using `uv export --format requirements-txt --no-hashes` with `pip-audit --no-deps --disable-pip -f json`. At audit time, the scan reported **no known vulnerabilities found** for the locked Python dependency set. One editable local project entry (`-e -`) could not be version-deduced by the tool and was excluded from vulnerability matching.

## Findings Summary

### 4.1 Risk Distribution

| Severity | Count |
|---|---:|
| Critical | 0 |
| High | 1 |
| Medium | 3 |
| Low | 0 |
| **Total** | **4** |

### 4.2 Findings Index

| ID | Title | Severity | CWE | Status |
|---|---|---|---|---|
| FINDING-001 | Known default admin password in container defaults | High | CWE-1392 | Open |
| FINDING-002 | JWT tokens persist in localStorage with unsafe-inline CSP | Medium | CWE-922 | Open |
| FINDING-003 | Import route returns raw backend exception details | Medium | CWE-209 | Open |
| FINDING-004 | Login endpoints lack brute-force throttling | Medium | CWE-307 | Open |

## Detailed Findings

### FINDING-001: Known default admin password in container defaults

| Attribute | Value |
|---|---|
| **ID** | FINDING-001 |
| **Severity** | High |
| **CWE** | CWE-1392 |
| **OWASP Top 10** | A05:2021 Security Misconfiguration |
| **Location** | `docker-compose.yml:31-32`, `backend/database.py:61-64` |
| **Status** | Open |

#### Description

The backend container defines a predictable fallback for `ADMIN_PASSWORD`, and the database bootstrap logic uses that environment variable to create or preserve the admin account. If the deployment omits an explicit override, the application can boot with a known administrative password.

#### Evidence

- `docker-compose.yml:31` sets `ADMIN_USERNAME: ${ADMIN_USERNAME:-admin}`
- `docker-compose.yml:32` sets `ADMIN_PASSWORD: ${ADMIN_PASSWORD:-admin_password_you_know_it}`
- `backend/database.py:61-64` reads those values and hashes the provided admin password during startup

#### Impact

An attacker who knows the default password can authenticate through `/admin-login`, read all student selection records, bulk overwrite student account data, and trigger administrative reminder actions.

#### Recommendation

Remove the fallback and fail closed when `ADMIN_PASSWORD` is missing or matches a known weak default. Use an explicit deployment-time secret or a one-time bootstrap flow.

#### References

- [CWE-1392](https://cwe.mitre.org/data/definitions/1392.html)
- [OWASP Top 10 A05:2021 Security Misconfiguration](https://owasp.org/Top10/A05_2021-Security_Misconfiguration/)

### FINDING-002: JWT tokens persist in localStorage with unsafe-inline CSP

| Attribute | Value |
|---|---|
| **ID** | FINDING-002 |
| **Severity** | Medium |
| **CWE** | CWE-922 |
| **OWASP Top 10** | A07:2021 Identification and Authentication Failures |
| **Location** | `frontend/login.html:4,39`, `frontend/admin-login.html:4,43`, `frontend/choose.html:59,79`, `frontend/admin.html:4,104,170,206` |
| **Status** | Open |

#### Description

The application stores bearer tokens in `localStorage` and then reads them back in subsequent privileged requests. At the same time, the frontend pages permit inline scripts via CSP. This combination increases the blast radius of any present or future script injection flaw.

#### Evidence

- `frontend/login.html:39-44` and `frontend/admin-login.html:43-44` write `jwt_token` to `localStorage`
- `frontend/choose.html:79` and `frontend/admin.html:104,170,206` read the token back into `Authorization` headers
- `frontend/login.html:4`, `frontend/admin-login.html:4`, `frontend/choose.html:4`, and `frontend/admin.html:4` allow `'unsafe-inline'` in `script-src`

#### Impact

If a script execution bug or compromised third-party script reaches the page, the attacker can exfiltrate the JWT and replay it against privileged endpoints. Admin-token theft would expose the full student dataset and batch-management functions.

#### Recommendation

Move the access token to an `HttpOnly` cookie or equivalent server-controlled storage and remove `'unsafe-inline'` from CSP by migrating inline scripts to nonce- or hash-based external scripts.

#### References

- [CWE-922](https://cwe.mitre.org/data/definitions/922.html)
- [OWASP Top 10 A07:2021 Identification and Authentication Failures](https://owasp.org/Top10/A07_2021-Identification_and_Authentication_Failures/)

### FINDING-003: Import route returns raw backend exception details

| Attribute | Value |
|---|---|
| **ID** | FINDING-003 |
| **Severity** | Medium |
| **CWE** | CWE-209 |
| **OWASP Top 10** | A05:2021 Security Misconfiguration |
| **Location** | `backend/main.py:269-273`, `frontend/admin.html:178-179` |
| **Status** | Open |

#### Description

The CSV import route catches arbitrary backend exceptions and sends `str(e)` back to the browser as an HTTP 500 detail. The admin UI then renders that raw value directly in the failure modal. This exposes internal implementation details to authenticated users.

#### Evidence

- `backend/main.py:273` raises `HTTPException(status_code=500, detail=str(e))`
- `frontend/admin.html:178-179` reads `err.detail` and displays it verbatim in the UI

#### Impact

The issue does not directly grant unauthorized access, but it can leak schema details, constraint names, and parsing behavior that help an attacker refine later payloads or probe backend internals.

#### Recommendation

Return a generic user-facing failure message and log the original exception server-side together with a request or job identifier for operator follow-up.

#### References

- [CWE-209](https://cwe.mitre.org/data/definitions/209.html)
- [OWASP Error Handling Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Error_Handling_Cheat_Sheet.html)

### FINDING-004: Login endpoints lack brute-force throttling

| Attribute | Value |
|---|---|
| **ID** | FINDING-004 |
| **Severity** | Medium |
| **CWE** | CWE-307 |
| **OWASP Top 10** | A07:2021 Identification and Authentication Failures |
| **Location** | `backend/main.py:89-128` |
| **Status** | Open |

#### Description

Both student and admin login endpoints validate password hashes and immediately return failure responses, but the code includes no failed-attempt counter, fixed delay, account lockout, or IP-based throttling. This leaves password guessing entirely to the strength of the chosen credentials.

#### Evidence

- `backend/main.py:89-101` implements `/login` with no rate-control logic
- `backend/main.py:112-127` implements `/admin-login` with no rate-control logic

#### Impact

Weak student passwords can be brute-forced at scale, and a compromised admin password would expose the full management surface and student dataset.

#### Recommendation

Add per-account and per-IP throttling, track failed attempts, and consider stronger controls such as admin-specific lockouts or MFA for the management login.

#### References

- [CWE-307](https://cwe.mitre.org/data/definitions/307.html)
- [OWASP Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)

## Remediation Priority

| Priority | Finding ID | Title | Severity | Estimated Effort | Notes |
|---:|---|---|---|---|---|
| 1 | FINDING-001 | Known default admin password in container defaults | High | Low | Remove dangerous runtime default before the next deployment |
| 2 | FINDING-002 | JWT tokens persist in localStorage with unsafe-inline CSP | Medium | High | Requires coordinated backend/frontend auth and CSP redesign |
| 3 | FINDING-004 | Login endpoints lack brute-force throttling | Medium | Medium | Add rate limiting and failure tracking at auth boundary |
| 4 | FINDING-003 | Import route returns raw backend exception details | Medium | Low | Replace raw exception output with generic error IDs |

## Appendix

### A. References

- [OWASP Top 10 (2021)](https://owasp.org/Top10/)
- [OWASP Web Security Testing Guide v4.2](https://owasp.org/www-project-web-security-testing-guide/)
- [OWASP Code Review Guide v2](https://owasp.org/www-project-code-review-guide/)
- [CWE - Common Weakness Enumeration](https://cwe.mitre.org/)

### B. Tools Used

| Tool | Purpose |
|---|---|
| Manual code review | Primary source-code review workflow |
| `owasp-audit` CLI | Audit lifecycle, finding validation, and report validation |
| `pip-audit` via `uvx` | Locked dependency vulnerability scan |

### C. Dependency Scan Result

- Command pattern: `uv export --format requirements-txt --no-hashes` + `pip-audit -r <exported-file> --no-deps --disable-pip -f json`
- Result: No known vulnerabilities found in the locked Python dependency set on 2026-04-06
- Limitation: the editable local project entry reported as `-e -` could not be matched to a package version by the tool

_Report prepared by: Codex_
_Date: 2026-04-06_
_Classification: Internal_

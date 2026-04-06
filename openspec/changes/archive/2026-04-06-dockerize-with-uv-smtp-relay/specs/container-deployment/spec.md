# container-deployment Specification

## Purpose

Defines requirements for the Docker Compose-based deployment architecture, including service topology, Python package management via uv, nginx static file serving, environment variable configuration, and Cloudflare Tunnel integration.

## ADDED Requirements

### Requirement: Docker Compose Service Topology

The system SHALL be fully deployable using `docker compose up --build -d` with four services: `db` (PostgreSQL), `backend` (FastAPI + Gunicorn), `nginx` (static files + API proxy), and `cloudflared` (Cloudflare Tunnel). All services SHALL communicate over a shared Docker internal network. The `backend` service SHALL depend on `db`, and `nginx` SHALL depend on `backend`, and `cloudflared` SHALL depend on `nginx`.

#### Scenario: Full stack starts successfully

- **WHEN** operator runs `docker compose up --build -d` with a valid `.env` file
- **THEN** all four services reach a running state, the application is accessible through the Cloudflare Tunnel URL, and the database is initialized with the admin user

#### Scenario: Backend waits for database

- **WHEN** `db` service is slow to start
- **THEN** `backend` service SHALL retry the database connection and not crash before `db` is ready

---

### Requirement: Python Dependency Management via uv

The system SHALL use `pyproject.toml` and `uv.lock` to declare and lock all Python dependencies. The `Dockerfile` for the backend SHALL install dependencies using `uv sync --frozen --no-dev`, ensuring bit-for-bit reproducible builds. `requirements.txt` SHALL be removed.

#### Scenario: Reproducible backend build

- **WHEN** the backend Docker image is built on any machine with the same `uv.lock`
- **THEN** the installed packages SHALL be identical to those on any other machine building from the same lock file

#### Scenario: Adding a new dependency

- **WHEN** a developer runs `uv add <package>`
- **THEN** `pyproject.toml` and `uv.lock` are updated, and the next `docker compose build` installs the new package

---

### Requirement: nginx Static File Serving

The `nginx` service SHALL serve all files in the `frontend/` directory as static assets. nginx SHALL map the following URL paths to their corresponding HTML files without requiring the `.html` extension: `/` → `index.html`, `/login` → `login.html`, `/choose` → `choose.html`, `/admin` → `admin.html`, `/admin-login` → `admin-login.html`.

#### Scenario: Student accesses login page

- **WHEN** a browser requests `GET /login`
- **THEN** nginx returns `login.html` with status 200

#### Scenario: Font file request

- **WHEN** a browser requests `/TW-Kai-98_1.ttf`
- **THEN** nginx returns the font file with the correct MIME type

---

### Requirement: nginx API Proxy

The `nginx` service SHALL proxy the following routes to `http://backend:8000`, preserving the original request method and body: `POST /login`, `POST /admin-login`, `POST /submit`, `GET /admin/all`, `POST /admin/import-students`, `POST /admin/send-reminders`. All other routes SHALL be handled as static files.

#### Scenario: Login API proxied correctly

- **WHEN** a browser sends `POST /login` with JSON credentials
- **THEN** nginx proxies the request to `backend:8000/login` and returns the backend response to the browser

#### Scenario: Static file takes precedence over proxy

- **WHEN** a browser sends `GET /choose`
- **THEN** nginx serves `choose.html` directly without contacting the backend

---

### Requirement: Frontend API URL Injection

The `frontend/config.js` file SHALL contain the placeholder string `__API_BASE_URL__` in place of any hardcoded URL. The nginx container's `entrypoint.sh` SHALL replace `__API_BASE_URL__` with the value of the `API_BASE_URL` environment variable at container startup using `sed`. When `API_BASE_URL` is empty (default), the frontend SHALL use relative paths.

#### Scenario: Production URL injection

- **WHEN** the nginx container starts with `API_BASE_URL=https://portal.school.edu.tw`
- **THEN** `config.js` at runtime contains `API_BASE_URL: "https://portal.school.edu.tw"`

#### Scenario: Default relative path

- **WHEN** the nginx container starts with `API_BASE_URL` unset or empty
- **THEN** `config.js` at runtime contains `API_BASE_URL: ""`, and all API calls use relative paths

---

### Requirement: Environment Variable Configuration

All runtime configuration SHALL be sourced from environment variables. A `.env.example` file SHALL document every required and optional environment variable with description and safe default values. The `docker-compose.yml` SHALL provide default values for non-secret variables (e.g., `SMTP_HOST`, `SMTP_PORT`, `DB_SSLMODE`, `TUNNEL_TRANSPORT_PROTOCOL`) so that the service starts with minimal `.env` configuration.

#### Scenario: Minimal .env for local development

- **WHEN** an operator creates a `.env` with only `SECRET_KEY`, `ADMIN_PASSWORD`, `SMTP_USER`, `SMTP_PASSWORD`, and `TUNNEL_TOKEN`
- **THEN** all services start and function correctly using Docker Compose default values for all other variables

#### Scenario: DB SSL mode override

- **WHEN** `DB_SSLMODE=require` is set in the environment
- **THEN** the backend connects to PostgreSQL with SSL required, and the connection fails if SSL is not available

---

### Requirement: Cloudflare Tunnel Integration

The `cloudflared` service SHALL authenticate with Cloudflare using the `TUNNEL_TOKEN` environment variable and run with `tunnel run --no-autoupdate`. The transport protocol SHALL be configurable via `TUNNEL_TRANSPORT_PROTOCOL` (values: `auto`, `quic`, `http2`; default: `auto`). The tunnel SHALL route incoming traffic to `http://nginx:80`.

#### Scenario: Tunnel connects on startup

- **WHEN** `cloudflared` starts with a valid `TUNNEL_TOKEN`
- **THEN** the service connects to Cloudflare and the configured public hostname resolves to the application

#### Scenario: Protocol fallback

- **WHEN** `TUNNEL_TRANSPORT_PROTOCOL=auto` and UDP is blocked on the network
- **THEN** cloudflared falls back to HTTP/2 over TCP and the tunnel remains operational

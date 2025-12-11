# CLAUDE.md - AI Agent Reference Guide

## ⚠️ CRITICAL INSTRUCTIONS:
- If you change the system architecture, add new major libraries, refactor the folder structure, or modify core design patterns, you MUST update this CLAUDE.md file to keep it current. This is the source of truth for all AI agents working on this codebase.
- Always use context7 when I need code generation, setup or configuration steps, or library/API documentation. This means you should automatically use the Context7 MCP tools to resolve library id and get library docs without me having to explicitly ask.

---

## Project Overview

**Collins-GPT** is a Flask-based web application that generates AI-powered "Dorothy Dixer" questions for parliamentary use. A Dorothy Dixer is a pre-arranged question asked in parliament to allow a minister to make a prepared response. The application uses OpenRouter's AI API (via OpenAI SDK) to generate contextual questions and answers based on user-provided topics, talking points, and strategic direction.

**Current State:** Early development (v0.1.0) - MVP with streaming AI generation, no database persistence or authentication.

---

## Architecture

### Application Pattern
- **Application Factory Pattern** (`app/__init__.py`): `create_app()` function creates and configures the Flask application
- **Blueprint-Based Routing** (`app/routes.py`): Single `main` blueprint organizes all routes
- **Service Layer Pattern** (`app/services/`): Business logic separated from HTTP handling, framework-agnostic

### Entry Point
- **File:** `main.py`
- **Server:** Flask development server (0.0.0.0:5000)
- **Startup:** `python main.py` or `uv run main.py`

### Technology Stack
- **Framework:** Flask 3.1.2+
- **Python Version:** 3.14+
- **Package Manager:** UV (modern alternative to pip/poetry)
- **Production Server:** Gunicorn 23.0.0+ (WSGI server for production)
- **Template Engine:** Jinja2 (Flask default)
- **Frontend:** Bootstrap 5.3.2 (CDN), Bootstrap Icons 1.11.1 (CDN)
- **Frontend Build Tools:**
  - **TypeScript:** 5.x+ (type-safe JavaScript)
  - **Vite:** 7.x+ (build tool with HMR)
  - **Package Manager:** pnpm (fast, disk-efficient)
  - **CSS Preprocessor:** SCSS/Sass
  - **Types:** @types/bootstrap for Bootstrap 5
- **AI API:** OpenRouter (via OpenAI SDK 2.9.0+)
- **Configuration:** python-dotenv for environment variables
- **Forms & CSRF:** Uses Flask-WTF / WTForms for server-side form validation and CSRF protection (see app/forms.py)
- **Deployment:** Google Cloud Run (serverless containers)

### Database & Persistence
**NONE** - Application is currently stateless. All data is ephemeral (exists only during request lifecycle).

### Services Architecture
**Services are framework-agnostic** - No Flask dependencies, pure Python business logic

### Configuration Management
- **Environment Variables:** `.env` file (loaded via python-dotenv)
  - `OPENROUTER_API_KEY` - Required for AI generation
**App Secrets:** `SECRET_KEY` is now loaded from the environment when available; update your `.env` in production.
  - ⚠️ **TODO:** Ensure `SECRET_KEY` is set in `.env` or environment for production deployments

### Frontend Architecture

**Source Location:** `frontend/src/` (TypeScript source files)
**Build Output:** `app/static/dist/` (production bundles, gitignored in dev)

**Module Organization:**
- **`main.ts`:** Entry point, initializes global modules
- **`modules/`:** Reusable UI modules (Bootstrap init, toasts, animations, smooth scrolling)
- **`pages/`:** Page-specific logic (government question writer with SSE streaming)
- **`types/`:** TypeScript type definitions (app types, Bootstrap types)
- **`styles/`:** SCSS files (Labor Party branding: #e11b22)

**Build Pipeline:**
1. TypeScript compiles to ES modules
2. Vite bundles and minifies (with tree-shaking)
3. SCSS compiles to CSS and is extracted/minified
4. Output to `app/static/dist/assets/` with content hashes

**Development Mode:**
- Vite dev server runs on `localhost:5173` with HMR
- Flask backend runs on `localhost:5000`
- Vite proxies API requests to Flask
- Templates load unbundled modules from Vite dev server via `vite_asset()` helper

**Production Mode:**
- Pre-build frontend: `cd frontend && pnpm run build:prod`
- Flask templates load hashed assets via `vite_asset()` helper
- Manifest file (`dist/.vite/manifest.json`) maps source paths to hashed filenames
- Bootstrap loaded from CDN (not bundled)

---

## Key Commands

### Package Management (UV)
```bash
# Install dependencies
uv sync

# Add a new dependency
uv add <package-name>

# Add a dev dependency
uv add --dev <package-name>

# Update dependencies
uv lock --upgrade
```

### Development Server
```bash
# Run development server (method 1)
python main.py

# Run development server (method 2)
uv run main.py

# Run with Flask CLI
export FLASK_APP=app
export FLASK_ENV=development
flask run
```

### Frontend Development
```bash
# Install frontend dependencies
cd frontend && pnpm install

# Run development servers (Flask + Vite) - RECOMMENDED
cd frontend && pnpm run dev

# Run Vite dev server only (requires Flask running separately)
cd frontend && pnpm run dev:vite

# Build for production
cd frontend && pnpm run build:prod

# Type check TypeScript
cd frontend && pnpm run type-check

# Clean build output
cd frontend && pnpm run clean
```

### Testing
**⚠️ NOT CURRENTLY CONFIGURED**
- No test framework installed (pytest/unittest)
- No test files exist
- `.gitignore` prepared for pytest (`.pytest_cache/`, `.coverage`, etc.)

**To add testing:**
```bash
uv add --dev pytest pytest-flask
# Create tests/ directory and write tests
pytest
```

### Type Checking
```bash
# Run Pyright (already configured as dev dependency)
uv run pyright

# VS Code has Pylance configured for inline type checking
```

---

## Code Style & Patterns

### Python Conventions
- **Type Hints:** Used throughout codebase (`Optional[str]`, `Generator[str, None, None]`, etc.)
- **Indentation:** 2 spaces (configured in `.vscode/settings.json`)
- **Docstrings:** Comprehensive Google-style docstrings with beginner-friendly explanations
- **Import Organization:** Auto-organized on save (VS Code)
- **Naming:**
  - Functions: `snake_case`
  - Classes: `PascalCase`
  - Constants: `UPPER_SNAKE_CASE`

### Flask Patterns
- **Blueprint Registration:** Done in application factory (`create_app()`)
- **Route Functions:** Return rendered templates or JSON/SSE responses
- **Business Logic:** NEVER in routes - always delegate to services
- **Error Handling:** Services raise exceptions, routes catch and format for HTTP responses

### Service Layer Principles
1. **Framework-Agnostic:** No Flask imports in services
2. **Pure Functions:** Prefer pure functions where possible
3. **Type Hints Required:** All function signatures must have type hints
4. **Comprehensive Docstrings:** Explain what, why, and how (especially for beginners)
5. **Generator Pattern:** Use generators for streaming/memory-efficient operations

### Frontend Patterns
- **Progressive Enhancement:** Works without JavaScript (where possible)
- **Bootstrap Components:** Use Bootstrap's built-in components before custom CSS
- **Event Handling:** Vanilla JavaScript (no jQuery)
- **State Management:** DOM-based state (data attributes, classes)

### Security Considerations
- **API Keys:** NEVER commit `.env` to version control (already in `.gitignore`)
- **Input Validation:** Client-side and server-side validation required
- **Secret Keys:** Move hardcoded secrets to environment variables

---

## Critical Areas for Future Development

### Missing Production-Ready Features
1. **Database Layer:** No persistence - consider SQLAlchemy + PostgreSQL/SQLite
2. **Authentication:** No user management - consider Flask-Login
3. **Testing:** No test coverage - add pytest + pytest-flask
4. **Error Logging:** Basic Flask logging - consider structured logging (Loguru, Python logging)
5. **Rate Limiting:** No API protection - consider Flask-Limiter
6. **Environment-Based Config:** Hardcoded values - create proper config classes
7. **Caching:** No response caching - consider Flask-Caching or Redis for OpenRouter responses

### Known Technical Debt
- No database models despite application needing to persist dixers
- No user authentication/authorization
- No caching layer (consider Flask-Caching for OpenRouter responses)
- No monitoring/observability (APM, error tracking)

---

## Deployment

### Google Cloud Run (Production)

The application is configured for deployment on Google Cloud Run, a fully managed serverless platform. See **[DEPLOY.md](./DEPLOY.md)** for comprehensive deployment instructions.

**Quick Deploy (with Secret Manager):**
```bash
# 1. Create secrets
echo -n "your-api-key" | gcloud secrets create openrouter-api-key --data-file=-
python -c "import secrets; print(secrets.token_hex(32), end='')" | gcloud secrets create flask-secret-key --data-file=-

# 2. Build frontend
cd frontend && pnpm install && pnpm run build:prod && cd ..

# 3. Deploy to Cloud Run (Sydney region, cost-optimized)
gcloud run deploy collins-gpt \
  --source . \
  --platform managed \
  --region australia-southeast1 \
  --allow-unauthenticated \
  --set-secrets OPENROUTER_API_KEY=openrouter-api-key:latest \
  --set-secrets SECRET_KEY=flask-secret-key:latest \
  --memory 256Mi \
  --cpu 1 \
  --min-instances 0 \
  --max-instances 10 \
  --timeout 300 \
  --cpu-throttling
```

**Key Files:**
- `Dockerfile` - Multi-stage build (frontend + Python with Gunicorn)
- `.dockerignore` - Excludes unnecessary files from Docker build
- `DEPLOY.md` - Complete deployment guide with Secret Manager, CI/CD, monitoring

**Production Requirements:**
- Gunicorn WSGI server (configured in Dockerfile)
- Google Secret Manager with secrets: `openrouter-api-key`, `flask-secret-key`
- Pre-built frontend assets in `app/static/dist/`
- Cost-optimized settings: 256Mi RAM, scale-to-zero, CPU throttling

**Expected Cost:** Likely **free** under Cloud Run's generous free tier (2M requests/month). Even with moderate traffic, typically under $5/month.

---

## Development Workflow

### Making Changes
1. **Read First:** Always read existing code before modifying
2. **Service Layer:** Business logic goes in `app/services/`, NOT in routes
3. **Type Hints:** Add type hints to all new functions
4. **Docstrings:** Write comprehensive docstrings for public functions
5. **Test Locally:** Run `python main.py` and test in browser
6. **Update This File:** If you change architecture, update CLAUDE.md

### Adding New Features
1. **Service First:** Create/modify service in `app/services/`
2. **Route Second:** Add route in `app/routes.py` that calls service
3. **Template Last:** Create/modify template in `app/templates/`
4. **Frontend:** Add TypeScript modules to `frontend/src/modules/` or page-specific code to `frontend/src/pages/`
5. **Styling:** Add SCSS to `frontend/src/styles/custom.scss` or create new SCSS files

### Adding Dependencies
```bash
# Production dependency
uv add <package-name>

# Development dependency
uv add --dev <package-name>

# This automatically updates pyproject.toml and uv.lock
```

---

## Environment Setup

### Required Environment Variables
Create `.env` in project root:
```env
OPENROUTER_API_KEY=your-api-key-here
```

### Python Version
**Python 3.14+** required (specified in `.python-version`)

### First-Time Setup
```bash
# Clone repository
git clone <repository-url>
cd collins-gpt

# Ensure Python 3.14+ is active
python --version

# Install dependencies with UV
uv sync

# Create .env file with API key
echo "OPENROUTER_API_KEY=your-key-here" > .env

# Run development server
python main.py

# Visit http://localhost:5000
```

---

## AI Agent Guidelines

### When Working on This Codebase
1. **Read CLAUDE.md first** - Understand current architecture
2. **Use the service layer** - Don't put business logic in routes
3. **Follow existing patterns** - Blueprint routes, service functions, Jinja2 templates
4. **Type everything** - Add type hints to all function signatures
5. **Document thoroughly** - Write beginner-friendly docstrings
6. **No database yet** - Application is stateless, don't assume persistence
7. **Update CLAUDE.md** - If you change core architecture, update this file

### Common Tasks
- **Add a new page:** Create route in `routes.py`, service in `services/`, template in `templates/`, TypeScript module in `frontend/src/pages/`
- **Add AI feature:** Extend `dixer_service.py` or create new service, use OpenRouter client pattern
- **Add styling:** Extend `frontend/src/styles/custom.scss`, maintain Labor Party red theme (#e11b22)
- **Add JavaScript:** Create TypeScript modules in `frontend/src/modules/` or page-specific code in `frontend/src/pages/`

### What NOT to Do
- ❌ Don't add database code (no ORM configured yet)
- ❌ Don't add authentication (not implemented yet)
- ❌ Don't commit `.env` file (contains API keys)
- ❌ Don't put business logic in routes (use services)
- ❌ Don't use pip/poetry for Python (this project uses UV)
- ❌ Don't use npm/yarn for frontend (this project uses pnpm)
- ❌ Don't add inline scripts to templates (use TypeScript modules)

---

**Last Updated:** 2025-12-11
**Version:** 0.1.0
**Maintainer:** AI Agent (Claude Code)

**🤖 REMINDER FOR AI AGENTS: Keep this file updated as the source of truth. If you refactor, add libraries, or change architecture, update CLAUDE.md immediately.**

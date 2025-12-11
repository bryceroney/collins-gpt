# Collins-GPT

A Flask-based web application that generates AI-powered "Dorothy Dixer" questions for parliamentary use, with a modern TypeScript/Vite frontend.

## Features

- **Flask Backend**: Lightweight Python web framework with service layer architecture
- **TypeScript Frontend**: Type-safe JavaScript with Vite build tooling
- **Bootstrap 5**: Modern, responsive CSS framework via CDN
- **Hot Module Replacement (HMR)**: Instant feedback during development
- **SCSS Preprocessing**: Organized styling with variables and nesting
- **UV Package Manager**: Fast, modern Python package management
- **pnpm**: Efficient Node.js package management
- **Server-Sent Events (SSE)**: Streaming AI responses
- **OpenRouter API**: AI-powered question generation

## Project Structure

```
collins-gpt/
├── app/
│   ├── __init__.py          # Application factory
│   ├── routes.py            # Route definitions (blueprints)
│   ├── services/            # Business logic layer
│   ├── forms.py             # WTForms form definitions
│   ├── vite_helpers.py      # Flask-Vite integration
│   ├── static/
│   │   └── dist/            # Vite build output (gitignored)
│   └── templates/
│       ├── base.html        # Base template
│       ├── dashboard.html   # Dashboard
│       └── government_question_writer.html
├── frontend/                # TypeScript/Vite frontend
│   ├── src/
│   │   ├── main.ts          # Entry point
│   │   ├── modules/         # Reusable UI modules
│   │   ├── pages/           # Page-specific logic
│   │   ├── types/           # TypeScript definitions
│   │   └── styles/          # SCSS files
│   ├── package.json
│   ├── tsconfig.json
│   └── vite.config.ts
├── main.py                  # Application entry point
├── pyproject.toml           # UV project configuration
└── .python-version          # Python version (3.14+)
```

## Prerequisites

- **Python 3.14+** - Backend runtime
- **Node.js 18+** - Frontend build tooling
- **UV** - Python package manager
- **pnpm** - Node.js package manager (faster than npm)

## Installation

### 1. Install UV (if not already installed)

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Or on Windows:

```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 2. Clone the Repository

```bash
git clone <repository-url>
cd collins-gpt
```

### 3. Install Python Dependencies

UV will automatically create a virtual environment and install dependencies:

```bash
uv sync
```

### 4. Install Frontend Dependencies

```bash
cd frontend
pnpm install
cd ..
```

### 5. Configure Environment Variables

Create a `.env` file in the project root:

```env
OPENROUTER_API_KEY=your-api-key-here
SECRET_KEY=your-secret-key-here
FLASK_ENV=development
```

**For GitHub Codespaces**, also add:

```env
VITE_DEV_SERVER_URL=https://your-codespace-name-5173.app.github.dev
```

Replace `your-codespace-name` with your actual Codespace name (visible in the forwarded ports panel).

## Running the Application

### Development Mode (Recommended)

**Option 1: Single Command (Concurrent Servers)**

From the `frontend/` directory, run both Flask and Vite servers together:

```bash
cd frontend
pnpm run dev
```

This starts:
- Flask backend on port **5000**
- Vite dev server on port **5173** with HMR

**Option 2: Separate Terminals**

Terminal 1 (Flask backend):
```bash
FLASK_ENV=development uv run python main.py
```

Terminal 2 (Vite frontend):
```bash
cd frontend
pnpm run dev:vite
```

### Accessing the Application

**Local Development:**
- Access Flask at: http://localhost:5000

**GitHub Codespaces:**
1. Forward port 5000 (Flask) - this will be your main access point
2. Forward port 5173 (Vite) - needed for HMR assets
3. Set `VITE_DEV_SERVER_URL` in `.env` to your Codespace's forwarded port 5173 URL
4. Access the app via the forwarded port 5000 URL

The Vite dev server provides:
- ⚡ **Hot Module Replacement** - instant updates without refresh
- 🔍 **TypeScript type checking** - catch errors before runtime
- 📦 **Fast rebuilds** - optimized development experience

### Production Deployment

**Step 1: Build Frontend Assets**

```bash
cd frontend
pnpm run build:prod
cd ..
```

This creates optimized, hash-versioned assets in `app/static/dist/`.

**Step 2: Run with Production WSGI Server**

```bash
# Add gunicorn to dependencies
uv add gunicorn

# Run with gunicorn
FLASK_ENV=production uv run gunicorn -w 4 -b 0.0.0.0:5000 "app:create_app()"
```

In production mode:
- Flask loads pre-built assets from `app/static/dist/`
- Assets have content hashes for cache busting
- No Vite dev server needed

## Configuration

### Environment Variables

Required variables in `.env`:

```env
# Required
OPENROUTER_API_KEY=your-openrouter-api-key
SECRET_KEY=your-secret-key-here

# Optional
FLASK_ENV=development

# GitHub Codespaces only
VITE_DEV_SERVER_URL=https://your-codespace-name-5173.app.github.dev
```

### Generating Secret Keys

```python
import secrets
print(secrets.token_hex(16))
```

## Development

### Frontend Development

#### TypeScript Type Checking

Run TypeScript type checks:

```bash
cd frontend
pnpm run type-check
```

This validates all TypeScript code without emitting files.

#### Frontend Commands

```bash
# Type check TypeScript
pnpm run type-check

# Build for production
pnpm run build:prod

# Preview production build
pnpm run preview

# Clean build artifacts
pnpm run clean
```

#### Project Structure

- **`frontend/src/main.ts`** - Entry point, initializes Bootstrap and utilities
- **`frontend/src/modules/`** - Reusable modules (toast, animations, etc.)
- **`frontend/src/pages/`** - Page-specific TypeScript (SSE streaming, forms)
- **`frontend/src/types/`** - TypeScript type definitions
- **`frontend/src/styles/`** - SCSS stylesheets

#### Adding New Frontend Features

1. **Create TypeScript module** in `frontend/src/modules/` or `frontend/src/pages/`
2. **Import in template** using `{{ vite_asset('path/to/module.ts') }}`
3. **Add styling** in `frontend/src/styles/custom.scss`

Example:
```html
{% block extra_js %}
<script type="module" src="{{ vite_asset('pages/my-new-page.ts') }}"></script>
{% endblock %}
```

### Backend Development (Python)

#### Code Quality and Type Checking

This project uses Pyright for Python type checking:

#### Install Pyright

```bash
# Using npm (requires Node.js)
npm install -g pyright

# Or using uv to add it as a dev dependency
uv add --dev pyright
```

#### Run Type Checks

```bash
# Run pyright on the entire project
pyright

# Run on specific files or directories
pyright app/
pyright app/routes.py

# Run with verbose output
pyright --verbose

# Generate a detailed report
pyright --outputjson
```

#### Configuration

The project uses the VSCode settings in `.vscode/settings.json` for type checking configuration:
- Type checking mode: `basic`
- Diagnostic mode: `workspace`
- Unused imports/variables: `information` level
- Type issues: `warning` level

You can also create a `pyrightconfig.json` in the project root for more granular command-line control:

```json
{
  "typeCheckingMode": "basic",
  "reportUnusedImport": "information",
  "reportUnusedVariable": "information",
  "reportGeneralTypeIssues": "warning",
  "pythonVersion": "3.14",
  "pythonPlatform": "Linux",
  "venvPath": ".",
  "venv": ".venv"
}
```

#### VSCode Integration

The project is configured with:
- 2-space indentation for all Python files
- Format on save
- Auto-organize imports on save
- Pylance language server with type checking enabled

### Adding New Pages

1. **Create service** in `app/services/` (business logic):
```python
def my_service_function():
    # Business logic here
    return result
```

2. **Add route** in `app/routes.py`:
```python
@bp.route('/new-page')
def new_page():
    result = my_service_function()
    return render_template('new_page.html', result=result)
```

3. **Create template** in `app/templates/`:
```html
{% extends "base.html" %}
{% block title %}New Page{% endblock %}
{% block content %}
<div class="container">
    <h1>New Page</h1>
</div>
{% endblock %}
```

4. **Add TypeScript** (if needed) in `frontend/src/pages/new-page.ts`

5. **Add styling** (if needed) in `frontend/src/styles/custom.scss`

### Adding Dependencies

**Python packages:**
```bash
uv add package-name              # Production
uv add --dev package-name        # Development
```

**Frontend packages:**
```bash
cd frontend
pnpm add -D package-name         # Development
pnpm add package-name            # Production (rare)
```

## Available Pages

- **Home** (`/`) - Landing page with features showcase
- **About** (`/about`) - About page with technology stack information
- **Contact** (`/contact`) - Contact page with form and information

## Technologies Used

### Backend
- **Flask** 3.1.2+ - Python web framework
- **OpenRouter API** - AI question generation
- **Flask-WTF** - Form handling and CSRF protection
- **UV** - Python package manager

### Frontend
- **TypeScript** 5.x+ - Type-safe JavaScript
- **Vite** 7.x+ - Build tool with HMR
- **Sass** - CSS preprocessing
- **Bootstrap** 5.3.2 (CDN) - CSS framework
- **Bootstrap Icons** 1.11.1 - Icon library
- **pnpm** - Node.js package manager

## Bootstrap Components Used

- Responsive navigation bar
- Card components
- Button styles
- Form controls
- Grid system
- Icons
- Alert messages
- Utilities

## Best Practices

- Application factory pattern for better testing and flexibility
- Blueprint organization for modular code
- Template inheritance to avoid duplication
- Static file organization
- Environment-based configuration
- Debug mode for development

## Troubleshooting

### GitHub Codespaces Issues

**Assets not loading:**
1. Check that port 5173 is forwarded (Vite dev server)
2. Set `VITE_DEV_SERVER_URL` in `.env` to your Codespace's forwarded port 5173 URL
3. Restart both servers

**Finding your Codespace URL:**
1. Open the Ports panel in VS Code
2. Find port 5173 in the list
3. Copy the "Forwarded Address"
4. Add to `.env` as `VITE_DEV_SERVER_URL=<copied-url>`

### Virtual Environment Issues

Remove `.venv` and reinstall:

```bash
rm -rf .venv
uv sync
```

### Frontend Build Issues

Clean and rebuild:

```bash
cd frontend
pnpm run clean
pnpm install
pnpm run build:prod
```

### Port Already in Use

Change ports in:
- **Flask**: Edit `main.py` - change port `5000`
- **Vite**: Edit `frontend/vite.config.ts` - change port `5173`

### TypeScript Errors

Run type check to see all errors:

```bash
cd frontend
pnpm run type-check
```

## License

MIT License

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## Support

For issues and questions, please open an issue in the repository.

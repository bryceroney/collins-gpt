# Flask Web Application

A modern, responsive web application built with Flask and Bootstrap 5, managed with UV package manager.

## Features

- **Flask Framework**: Lightweight and flexible Python web framework
- **Bootstrap 5**: Modern, responsive CSS framework via CDN
- **UV Package Manager**: Fast, modern Python package management
- **Application Factory Pattern**: Clean, modular architecture
- **Blueprint-based Routing**: Organized route management
- **Jinja2 Templates**: Powerful templating with template inheritance
- **Responsive Design**: Mobile-first design with Bootstrap 5
- **Custom CSS/JS**: Extensible styling and functionality

## Project Structure

```
collins-gpt/
├── app/
│   ├── __init__.py          # Application factory
│   ├── routes.py            # Route definitions
│   ├── static/
│   │   ├── css/
│   │   │   └── custom.css   # Custom styles
│   │   └── js/
│   │       └── custom.js    # Custom JavaScript
│   └── templates/
│       ├── base.html        # Base template with Bootstrap 5
│       ├── index.html       # Home page
│       ├── about.html       # About page
│       └── contact.html     # Contact page
├── main.py                  # Application entry point
├── pyproject.toml           # UV project configuration
└── .python-version          # Python version specification
```

## Prerequisites

- Python 3.14 or higher
- UV package manager

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

### 3. Install Dependencies

UV will automatically create a virtual environment and install dependencies:

```bash
uv sync
```

## Running the Application

### Development Server

Run the Flask development server:

```bash
uv run python main.py
```

Or use the UV shorthand:

```bash
uv run main.py
```

The application will be available at:
- Local: http://127.0.0.1:5000
- Network: http://0.0.0.0:5000

### Production Deployment

For production, use a WSGI server like Gunicorn:

```bash
# Add gunicorn to dependencies
uv add gunicorn

# Run with gunicorn
uv run gunicorn -w 4 -b 0.0.0.0:5000 "app:create_app()"
```

## Configuration

### Environment Variables

Create a `.env` file in the root directory:

```env
FLASK_APP=main.py
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
```

### Secret Key

For production, generate a secure secret key:

```python
import secrets
print(secrets.token_hex(16))
```

Update the secret key in `app/__init__.py`.

## Development

### Code Quality and Type Checking

This project is configured with Pylance for type checking and style validation in VSCode. To run these checks from the command line, use `pyright` (the command-line version of Pylance):

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

### Adding New Routes

1. Add routes to `app/routes.py`:

```python
@bp.route('/new-page')
def new_page():
    return render_template('new_page.html')
```

2. Create the corresponding template in `app/templates/`:

```html
{% extends "base.html" %}

{% block title %}New Page{% endblock %}

{% block content %}
<div class="container">
    <h1>New Page</h1>
</div>
{% endblock %}
```

### Adding Dependencies

Use UV to add new Python packages:

```bash
uv add package-name
```

### Custom Styling

Add your custom CSS to `app/static/css/custom.css` or create new CSS files and link them in your templates.

### Custom JavaScript

Add your custom JavaScript to `app/static/js/custom.js` or create new JS files and link them in your templates.

## Available Pages

- **Home** (`/`) - Landing page with features showcase
- **About** (`/about`) - About page with technology stack information
- **Contact** (`/contact`) - Contact page with form and information

## Technologies Used

- **Backend**: Flask 3.1.2
- **Frontend**: Bootstrap 5.3.2 (via CDN)
- **Icons**: Bootstrap Icons 1.11.1
- **Template Engine**: Jinja2
- **Package Manager**: UV

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

### Virtual Environment Issues

If you encounter virtual environment issues, remove the `.venv` folder and run:

```bash
uv sync
```

### Port Already in Use

If port 5000 is already in use, modify `main.py` to use a different port:

```python
app.run(debug=True, host='0.0.0.0', port=8000)
```

### Import Errors

Make sure you're running the application using `uv run`:

```bash
uv run python main.py
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

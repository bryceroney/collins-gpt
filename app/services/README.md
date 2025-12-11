# Services Directory

This directory contains the **business logic** (the "brains") of the CollinsGPT application.

## What are Services?

In web development, we separate our code into layers:
- **Routes** (in `routes.py`): Handle HTTP requests and responses - they're like receptionists
- **Services** (in this directory): Do the actual work - they're like the specialists
- **Templates** (in `templates/`): Display the results to users - they're like the presentation

This separation makes our code:
- **Easier to understand**: Each file has one clear purpose
- **Easier to test**: We can test business logic without a web browser
- **Easier to reuse**: Multiple routes can use the same service functions

## Files in This Directory

### `__init__.py`
An empty file that tells Python this directory is a "package" (a collection of modules).
You need this file for Python to allow imports from this directory.

### `openai_client.py`
Manages the connection to OpenRouter (the AI service provider).

**Functions:**
- `get_openai_client()`: Creates a client to talk to the AI
- `check_api_key_configured()`: Checks if we have an API key set up

**Why separate this?**
If we ever want to switch AI providers or change how we configure the client,
we only need to edit this one file.

### `dixer_service.py`
Contains all the logic for generating parliamentary questions and answers.

**Functions:**
- `build_user_prompt()`: Formats the user's input into a prompt for the AI
- `parse_dixer_response()`: Splits the AI's response into question and answer parts
- `calculate_max_tokens()`: Figures out how much text the AI should generate
- `generate_dixer()`: Main function - generates a complete question and answer (non-streaming)
- `generate_dixer_stream()`: Same as above, but sends results piece-by-piece as they're generated

**Why separate this?**
All the AI logic is in one place. If we want to add more AI tools (like the "Hot Issues Brief Updater"),
we can create similar service files following the same pattern.

## How Routes Use Services

Here's a simplified example of how `routes.py` uses these services:

```python
# In routes.py
from .services.openai_client import check_api_key_configured
from .services.dixer_service import generate_dixer

@bp.route('/dixer-writer', methods=['POST'])
def dixer_writer():
    # 1. Check prerequisites
    if not check_api_key_configured():
        return "Error: API key not set"

    # 2. Get user input
    topic = request.form.get('topic')

    # 3. Call the service to do the work
    result = generate_dixer(topic=topic, word_count=200)

    # 4. Return the result to the user
    return render_template('dixer_writer.html', result=result)
```

Notice how the route just coordinates - it doesn't know anything about AI prompts or API calls.
All that complexity is hidden in the service layer.

## Best Practices for Services

1. **Single Responsibility**: Each function should do one thing well
2. **No Flask Dependencies**: Services shouldn't import Flask's `request` or `render_template`
   - This makes them testable without a web server
3. **Type Hints**: Use type hints (like `str`, `int`, `Optional[str]`) to document what each function expects
4. **Docstrings**: Every function should have a docstring explaining what it does
5. **Error Handling**: Services should raise exceptions; routes should catch and handle them

## For Python Beginners

If you're new to Python, here are some concepts you'll see in these files:

### Imports
```python
from .openai_client import get_openai_client
```
- The `.` means "from this package" (the current directory)
- We're importing the `get_openai_client` function from `openai_client.py`

### Type Hints
```python
def build_prompt(topic: str, word_count: int) -> str:
```
- `topic: str` means topic should be a string
- `word_count: int` means word_count should be an integer
- `-> str` means this function returns a string
- These are optional but help catch bugs!

### Optional Values
```python
member_name: Optional[str] = None
```
- `Optional[str]` means this can be a string OR None (missing)
- `= None` sets the default value if not provided

### Generators
```python
def generate_stream() -> Generator[str, None, None]:
    yield "chunk 1"
    yield "chunk 2"
```
- Generators return values one at a time using `yield`
- They're memory-efficient for large amounts of data
- Used for streaming responses

### Docstrings
```python
def my_function():
    """
    This is a docstring - it documents what the function does.

    Args:
        param1: What this parameter is for

    Returns:
        What this function gives back
    """
```
- Always read the docstring first to understand a function
- Triple quotes (`"""`) let you write multi-line strings

## Adding New Services

When you want to add a new AI tool:

1. Create a new file in this directory (e.g., `hot_issues_service.py`)
2. Follow the same pattern as `dixer_service.py`:
   - Import the OpenAI client
   - Define your prompts as constants
   - Create functions for building prompts, parsing responses, and generating content
   - Add comprehensive docstrings
3. Import and use it in `routes.py`

Example:
```python
# In app/services/hot_issues_service.py
from .openai_client import get_openai_client

HOT_ISSUES_PROMPT = """..."""

def generate_brief(sources: list[str]) -> dict:
    """Generate a brief from news sources."""
    client = get_openai_client()
    # ... rest of the logic
    return result
```

Then in routes:
```python
from .services.hot_issues_service import generate_brief

@bp.route('/hot-issues')
def hot_issues():
    result = generate_brief(sources=get_news_sources())
    return render_template('hot_issues.html', result=result)
```

## Questions?

If you're confused about anything:
1. Read the docstrings in each file
2. Look at how `routes.py` uses the services
3. Try adding print statements to see what's happening
4. Ask questions in the project issues/discussions

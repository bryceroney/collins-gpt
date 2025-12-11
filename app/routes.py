"""
Flask Routes for CollinsGPT

This module defines all the URL routes (endpoints) for our web application.
Routes are like the "pages" of our website - each URL the user can visit.

For Python beginners:
- A route is a URL pattern (like '/about' or '/contact')
- When a user visits a URL, Flask calls the associated function
- The function returns HTML that gets displayed in the browser
- We use Blueprint to organize related routes together
"""

from datetime import datetime
from flask import Blueprint, render_template, request, Response, stream_with_context

# Import our service modules (the business logic)
from .services.openai_client import check_api_key_configured
from .services.dixer_service import generate_dixer_stream

# Create a Blueprint - a way to organize related routes
# Think of it like a mini-application within our main Flask app
bp = Blueprint('main', __name__)


def get_greeting():
  """
  Return a time-appropriate greeting based on the current hour.

  This is a simple helper function that makes our dashboard feel more personal.

  Returns:
    str: "Good Morning", "Good Afternoon", or "Good Evening"

  For Python beginners:
  - datetime.now() gets the current date and time
  - .hour extracts just the hour (0-23)
  - We use if/elif/else to choose the right greeting
  """
  hour = datetime.now().hour
  if hour < 12:
    return "Good Morning"
  elif hour < 17:
    return "Good Afternoon"
  else:
    return "Good Evening"


@bp.route('/')
def index():
  """
  Display the main dashboard page.

  This is the home page of our application. It shows all available AI modules
  as cards that users can click to launch.

  Returns:
    str: Rendered HTML for the dashboard page

  For Python beginners:
  - @bp.route('/') is a decorator - it tells Flask this function handles the '/' URL
  - The function name ('index') doesn't have to match the URL
  - render_template() loads an HTML file and fills in any variables
  """
  # Define the modules that will appear on the dashboard
  # This is a list of dictionaries - each dict represents one module card
  modules = [
    {
      "id": "government-question-writer",
      "title": "Government Question Writer",
      "description": "Generates questions for Government MPs to ask during Question Time.",
      "icon": "bi-mic-fill",
      "color": "primary",
      "url": "main.government_question_writer"  # Points to the government_question_writer function below
    },
    {
      "id": "hot-issues",
      "title": "Hot Issues Brief Updater",
      "description": "Scans the latest news to update the daily briefing notes on emerging issues.",
      "icon": "bi-newspaper",
      "color": "info",
      "url": None  # None means not yet implemented - will show "Coming Soon"
    }
  ]

  # Render the template and pass in our data
  return render_template(
    'dashboard.html',
    greeting=get_greeting(),
    modules=modules,
    active_page='dashboard'
  )


@bp.route('/government-question-writer')
def government_question_writer():
  """
  Display the Dixer Writer page.

  This shows the form where users can input details to generate a Dorothy Dixer.

  Returns:
    str: Rendered HTML for the dixer writer page
  """
  # Provide default form values
  form_data = {
    'word_count': 200,
    'topic': '',
    'member_name': '',
    'electorate': '',
    'strategy': 'option_a',
    'model': 'anthropic/claude-sonnet-4.5'
  }
  return render_template('government_question_writer.html', form_data=form_data, active_page='government_question_writer')


@bp.route('/government-question-writer/stream', methods=['POST'])
def government_question_writer_stream():
  """
  Handle streaming generation of Dixers.

  This is the streaming version of the dixer writer. Instead of waiting for
  the complete response, it sends the AI's output word-by-word as it's generated.
  This provides a much better user experience.

  This route only accepts POST requests with JSON data (not HTML form data).
  The frontend JavaScript calls this route and displays the streaming response.

  Returns:
    Response: A streaming response with Server-Sent Events (SSE)

  For Python beginners:
  - This function is different because it returns a stream, not HTML
  - Server-Sent Events (SSE) is a way to send data from server to browser continuously
  - The browser can display each "chunk" as it arrives
  - This is how ChatGPT shows responses appearing word-by-word
  """
  # Get the JSON data sent by the frontend JavaScript
  # request.get_json() parses JSON into a Python dictionary
  data = request.get_json()

  # Extract all the parameters from the JSON
  # .get() safely gets a value, returning a default if the key doesn't exist
  word_count = int(data.get('word_count', 200))
  topic = data.get('topic', '').strip()
  member_name = data.get('member_name', '').strip()
  electorate = data.get('electorate', '').strip()
  strategy = data.get('strategy', 'option_a')
  model = data.get('model', 'anthropic/claude-sonnet-4.5')

  # Validate required fields
  if not topic:
    # Return an error event in SSE format
    return Response(
      f"data: {{'error': 'Please provide a topic or announcement.'}}\n\n",
      mimetype='text/event-stream'
    )

  if not check_api_key_configured():
    return Response(
      f"data: {{'error': 'OpenRouter API key not configured.'}}\n\n",
      mimetype='text/event-stream'
    )

  # Call the streaming service function
  # This returns a generator that yields SSE-formatted strings
  stream = generate_dixer_stream(
    topic=topic,
    word_count=word_count,
    strategy=strategy,
    member_name=member_name if member_name else None,
    electorate=electorate if electorate else None,
    model=model
  )

  # Return the stream as a Response
  # stream_with_context() ensures the stream has access to Flask's request context
  # mimetype='text/event-stream' tells the browser this is SSE
  return Response(
    stream_with_context(stream),
    mimetype='text/event-stream',
    headers={
      'Cache-Control': 'no-cache',  # Don't cache streaming responses
      'X-Accel-Buffering': 'no'     # Disable buffering in nginx (if used)
    }
  )

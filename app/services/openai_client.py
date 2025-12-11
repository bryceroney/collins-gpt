"""
OpenAI/OpenRouter Client Configuration Service

This module handles the setup and configuration of the OpenAI client that we use
to connect to OpenRouter (a service that provides access to multiple AI models).

For Python beginners:
- A module is just a Python file that contains related functions and classes
- We use this module to centralize our AI client setup in one place
- This follows the "separation of concerns" principle - keeping related code together
"""

import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
# Environment variables are a secure way to store API keys and configuration
# They're stored in a .env file that should NEVER be committed to git
load_dotenv()


def get_openai_client():
    """
    Create and return a configured OpenAI client for OpenRouter.

    This function creates a client that connects to OpenRouter instead of OpenAI directly.
    OpenRouter acts as a gateway to multiple AI models (Claude, GPT-4, etc).

    Returns:
        OpenAI: A configured OpenAI client object that can make API calls.

    Example:
        >>> client = get_openai_client()
        >>> response = client.chat.completions.create(...)

    For Python beginners:
    - A function is a reusable block of code that performs a specific task
    - The 'return' statement sends a value back to whoever called the function
    - Triple-quoted strings are docstrings - they document what the function does
    """
    client = OpenAI(
        # base_url tells the client to connect to OpenRouter instead of OpenAI
        base_url="https://openrouter.ai/api/v1",

        # api_key is read from the OPENROUTER_API_KEY environment variable
        # os.getenv() returns the value, or "" (empty string) if it doesn't exist
        api_key=os.getenv("OPENROUTER_API_KEY", ""),
    )
    return client


def check_api_key_configured():
    """
    Check if the OpenRouter API key is configured.

    This is a helper function to validate that we have an API key before
    trying to make requests. It's better to check early and give a clear
    error message than to fail later with a confusing error.

    Returns:
        bool: True if the API key is set, False otherwise.

    Example:
        >>> if not check_api_key_configured():
        ...     print("Please set OPENROUTER_API_KEY environment variable")

    For Python beginners:
    - 'bool' means boolean - a value that's either True or False
    - We use this kind of check to validate prerequisites before proceeding
    """
    api_key = os.getenv("OPENROUTER_API_KEY", "")
    # This returns True if api_key has a value, False if it's empty
    return bool(api_key)

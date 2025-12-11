"""
Dixer Writer Service

This module contains all the business logic for generating parliamentary "Dorothy Dixer"
questions and answers using AI.

What is a Dorothy Dixer?
A "Dorothy Dixer" is a pre-arranged question asked in parliament that allows the
government to showcase their policies. It's called "friendly" because it's designed
to make the Minister look good.

For Python beginners:
- This is a "service" module - it contains the core business logic of our application
- We separate this from routes.py to keep our code organized and testable
- Each function has a single, well-defined purpose
"""

import json
from typing import Dict, Generator, Optional
from .openai_client import get_openai_client


# System Prompt - This tells the AI how to behave and what rules to follow
# It's like giving instructions to a speechwriter about the style and format
DIXER_SYSTEM_PROMPT = """You are an expert parliamentary speechwriter for the Australian Federal Government. Your task is to draft 'Dorothy Dixer' questions and ministerial answers following strict style guidelines.

### Guidance for Drafting 'Dorothy Dixer' Questions and Answers
**Model: Friendly Government Question & Minister Collins Style Response**

**1. The Structure of the Question**
* **Constraint:** No arguments or imputations. Must ask *about* policy.
* **Option A (Good News):**
  1. Address: "My question is to the Minister for [Portfolio]."
  2. Setup: "How is the Albanese Labor government [positive verb] [policy area]?"
  3. Link: "Why is this important for [specific group]?"
* **Option B (Contrast):**
  1. Address: "My question is to the Minister for [Portfolio]."
  2. Setup: "How is the Albanese Labor government delivering [policy outcome]?"
  3. Trigger: "How does this differ from other approaches?" (Keep neutral).

**2. The Structure of the Answer (Minister Collins Style)**
* **Phase 1: The Personal Praise (Mandatory):**
  * If the Member's name and electorate are provided: "I want to thank the terrific member for [Electorate]. She/He is a terrific representative who is always out there engaging with [stakeholders]..."
  * If the Member's name/electorate are NOT provided: Use placeholder text exactly as written: "I want to thank the member for [ELECTORATE] for their question." (Keep the brackets so it can be filled in later)
* **Phase 2: The Action Body:** Pivot to government action. Keywords: "Careful and considered," "restoring our place," "working night and day."
* **Phase 3: The Closing:**
  * If Option A: Reiterate benefits ("real and tangible benefits").
  * If Option B: Attack the Opposition ("cleaning up the mess," "reckless arrogance").

**Output Format:**
You must structure your response with clear sections:
1. First output the QUESTION (what the backbencher will ask)
2. Then output the ANSWER (what Minister Collins will respond)

Use these exact headers:
## QUESTION
[The question text]

## ANSWER
[The answer text]

**IMPORTANT - Formatting:**
- Break the ANSWER into multiple short paragraphs (3-5 sentences each) for readability.
- Use a blank line between each paragraph.
- Structure the answer with clear visual breaks between:
 1. The personal praise opening
 2. Each major policy point or action
 3. The closing statement
- This makes it easier for the Minister to read and deliver naturally.
"""


def build_user_prompt(
  topic: str,
  word_count: int,
  strategy: str = "option_a",
  member_name: Optional[str] = None,
  electorate: Optional[str] = None
) -> str:
  """
  Build the user prompt that will be sent to the AI.

  This function takes all the user's input and formats it into a clear prompt
  that the AI can understand.

  Args:
    topic (str): The policy topic or announcement to write about.
    word_count (int): Target number of words for the answer.
    strategy (str): Either "option_a" (positive) or "option_b" (attack).
           Defaults to "option_a".
    member_name (Optional[str]): Name of the MP asking the question.
                  Optional - can be None.
    electorate (Optional[str]): The MP's electorate.
                 Optional - can be None.

  Returns:
    str: A formatted prompt ready to send to the AI.

  For Python beginners:
  - Args: means "arguments" - the inputs this function needs
  - Optional[str] means the value can be a string or None (missing)
  - The -> str part tells you this function returns a string
  - f-strings (f"...") let you insert variables into strings using {variable}
  """
  # Determine which strategy text to show
  strategy_text = (
    "Option A: Good News (Positive)"
    if strategy == "option_a"
    else "Option B: Contrast (Attack)"
  )

  # Handle personalization vs placeholder
  # If we have member details, personalize. Otherwise, use placeholder.
  if member_name and electorate:
    member_info = f"""**Member Asking:** {member_name}

**Member's Electorate:** {electorate}

Please personalise the answer with specific praise for this member and their electorate."""
  else:
    member_info = """**Member Asking:** Not specified

**Member's Electorate:** Not specified

Since the member is not specified, use placeholder text in the answer opening: "I want to thank the member for [ELECTORATE] for their question." Keep the brackets as a placeholder to be filled in later."""

  # Build the final prompt using an f-string
  # The triple quotes let us write multi-line strings
  user_prompt = f"""Please draft a Dorothy Dixer question and ministerial answer with the following details:

**Topic/Announcement:** {topic}

{member_info}

**Strategy:** {strategy_text}

**Target Answer Length:** Approximately {word_count} words for the answer (the question can be shorter, but aim for around {word_count} words in the Minister's answer).

Generate a parliamentary question following the {strategy_text.split(':')[0]} structure, and a Minister Collins-style answer."""

  return user_prompt


def parse_dixer_response(response_text: str) -> Dict[str, str]:
  """
  Parse the AI's response into separate question and answer sections.

  The AI returns the question and answer together. This function splits them
  into two parts so we can display them separately.

  Args:
    response_text (str): The raw text response from the AI.

  Returns:
    Dict[str, str]: A dictionary with three keys:
           - 'question': The extracted question text
           - 'answer': The extracted answer text
           - 'raw': The original full response

  For Python beginners:
  - Dict[str, str] means a dictionary (like a lookup table) where both
   keys and values are strings
  - We use dictionaries to group related data together
  - Example: {"question": "...", "answer": "..."}
  """
  # Create the result dictionary with default empty values
  result = {
    'question': '',
    'answer': '',
    'raw': response_text
  }

  # Try to split by the standard headers the AI should use
  if '## QUESTION' in response_text and '## ANSWER' in response_text:
    # Split the text at "## ANSWER"
    parts = response_text.split('## ANSWER')

    # The first part contains "## QUESTION" and the question text
    question_part = parts[0].replace('## QUESTION', '').strip()

    # The second part (if it exists) is the answer
    answer_part = parts[1].strip() if len(parts) > 1 else ''

    result['question'] = question_part
    result['answer'] = answer_part
  else:
    # Fallback: Try other common patterns if the AI didn't use headers
    lower_text = response_text.lower()
    if 'question:' in lower_text and 'answer:' in lower_text:
      # Find the positions of these words
      q_idx = lower_text.find('question:')
      a_idx = lower_text.find('answer:')

      # Only split if question comes before answer
      if q_idx < a_idx:
        result['question'] = response_text[q_idx + 9:a_idx].strip()
        result['answer'] = response_text[a_idx + 7:].strip()
    else:
      # Last resort: treat the whole thing as the answer
      result['answer'] = response_text

  return result


def calculate_max_tokens(word_count: int) -> int:
  """
  Calculate how many tokens to request from the AI based on desired word count.

  Tokens are the units AI models use to measure text. Roughly:
  - 1 word ≈ 1.3-1.5 tokens in English
  - We multiply by 2 to give the AI plenty of room
  - We add 500 extra for the question and formatting
  - We cap at 4000 to avoid excessive API costs

  Args:
    word_count (int): Target number of words for the answer.

  Returns:
    int: The number of tokens to request from the API.

  For Python beginners:
  - min() returns the smaller of two numbers
  - This prevents us from requesting too many tokens (which costs money)
  """
  return min(word_count * 2 + 500, 4000)


def generate_dixer_stream(
  topic: str,
  word_count: int,
  strategy: str = "option_a",
  member_name: Optional[str] = None,
  electorate: Optional[str] = None
) -> Generator[str, None, None]:
  """
  Generate a Dixer with streaming (word-by-word) response.

  This is similar to generate_dixer() but returns results incrementally
  as the AI generates them, instead of waiting for the complete response.
  This provides a better user experience for long responses.

  Args:
    topic (str): The policy topic or announcement.
    word_count (int): Target word count for the answer.
    strategy (str): "option_a" (positive) or "option_b" (attack).
    member_name (Optional[str]): Name of the MP (optional).
    electorate (Optional[str]): The MP's electorate (optional).

  Yields:
    str: Server-Sent Event (SSE) formatted strings, each containing
      a JSON payload with either:
      - {"chunk": "text"} for partial responses
      - {"done": true, "question": "...", "answer": "..."} when complete
      - {"error": "message"} if something goes wrong

  For Python beginners:
  - Generator[str, None, None] means this function yields (returns)
   multiple strings over time, not just one
  - 'yield' is like 'return' but the function continues running
  - This is useful for streaming data as it becomes available
  - Generators are memory-efficient for large amounts of data
  """
  try:
    # Get the configured AI client
    client = get_openai_client()

    # Build the prompt
    user_prompt = build_user_prompt(
      topic=topic,
      word_count=word_count,
      strategy=strategy,
      member_name=member_name,
      electorate=electorate
    )

    # Calculate token limit
    max_tokens = calculate_max_tokens(word_count)

    # Make the streaming API call
    # Note: stream=True means we get results piece by piece
    stream = client.chat.completions.create(
      model="anthropic/claude-sonnet-4",
      messages=[
        {"role": "system", "content": DIXER_SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt}
      ],
      temperature=0.7,
      max_tokens=max_tokens,
      stream=True  # This enables streaming!
    )

    # Accumulate the full response as we stream
    full_response = ""

    # Process each chunk as it arrives
    # 'for chunk in stream' loops through each piece the AI sends
    for chunk in stream:
      # Check if this chunk has content
      if chunk.choices[0].delta.content:
        content = chunk.choices[0].delta.content
        full_response += content

        # Send this chunk to the client as a Server-Sent Event
        # json.dumps() converts our Python dict to JSON format
        yield f"data: {json.dumps({'chunk': content})}\n\n"

    # When streaming is complete, parse the full response
    parsed = parse_dixer_response(full_response)

    # Send the final parsed result
    yield f"data: {json.dumps({'done': True, 'question': parsed['question'], 'answer': parsed['answer']})}\n\n"

  except Exception as e:
    # If anything goes wrong, send an error event
    # str(e) converts the error to a string message
    yield f"data: {json.dumps({'error': str(e)})}\n\n"

import os

from dotenv import load_dotenv
from google import genai


# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")


# ============================================================
# CREATE GEMINI CLIENT
# ============================================================

client = None

if API_KEY:
    client = genai.Client(api_key=API_KEY)


# ============================================================
# AI DEBUGGING FUNCTION
# ============================================================

def get_ai_debugging_help(
    code,
    error_type="",
    error_message="",
    line=""
):
    """
    Send Python code and detected error information to Gemini.

    Returns a beginner-friendly AI debugging explanation.
    """

    # --------------------------------------------------------
    # Check API key
    # --------------------------------------------------------

    if not API_KEY:
        return (
            "Gemini AI is not configured yet.\n\n"
            "Please add the following to the .env file "
            "in the DebugGenie folder:\n\n"
            "GEMINI_API_KEY=YOUR_API_KEY"
        )

    # --------------------------------------------------------
    # Check Gemini client
    # --------------------------------------------------------

    if client is None:
        return (
            "Gemini client could not be initialized.\n\n"
            "Please check your GEMINI_API_KEY."
        )

    # --------------------------------------------------------
    # Prompt
    # --------------------------------------------------------

    prompt = f"""
You are DebugGenie, an AI-powered Python debugging assistant.

Your job is to help a beginner understand and fix Python errors.

Analyze the following code.

================ PYTHON CODE ================

{code}

================ ERROR INFORMATION ================

Error Type:
{error_type}

Error Message:
{error_message}

Error Line:
{line}

=====================================================

Give a clear and beginner-friendly explanation.

Use exactly these sections:

1. What is the error?
Explain what the error means.

2. Why did it happen?
Explain why the given code produced this error.

3. How to fix it?
Give simple steps to fix the problem.

4. Corrected code
Show the corrected Python code.

Important:
- Do not invent errors.
- Focus on the actual error.
- Keep the explanation understandable for a beginner.
- If the code is already correct, explain that no basic error was detected.
"""

    # ========================================================
    # SEND REQUEST TO GEMINI
    # ========================================================

    try:

        response = client.models.generate_content(
            model="gemini-3.8-flash",
            contents=prompt
        )

        # ----------------------------------------------------
        # Check response
        # ----------------------------------------------------

        if response and response.text:
            return response.text

        return "Gemini returned an empty response."

    # ========================================================
    # ERROR HANDLING
    # ========================================================

    except Exception as error:

        error_text = str(error)

        # ----------------------------------------------------
        # 503 - Temporary service unavailable
        # ----------------------------------------------------

        if "503" in error_text or "UNAVAILABLE" in error_text:
            return (
                "Gemini AI is temporarily unavailable.\n\n"
                "The Gemini model is currently experiencing "
                "high demand. Please try again in a few moments.\n\n"
                "Your local DebugGenie analysis is still available."
            )

        # ----------------------------------------------------
        # 401 - Authentication error
        # ----------------------------------------------------

        if "401" in error_text or "UNAUTHENTICATED" in error_text:
            return (
                "Gemini authentication failed.\n\n"
                "Please check your GEMINI_API_KEY in the "
                ".env file."
            )

        # ----------------------------------------------------
        # 403 - Permission error
        # ----------------------------------------------------

        if "403" in error_text or "PERMISSION_DENIED" in error_text:
            return (
                "Gemini access was denied.\n\n"
                "Please check that your API key has permission "
                "to use the Gemini API."
            )

        # ----------------------------------------------------
        # 404 - Model not found
        # ----------------------------------------------------

        if "404" in error_text or "NOT_FOUND" in error_text:
            return (
                "The Gemini model is currently unavailable "
                "for this API key.\n\n"
                "Please check the selected Gemini model."
            )

        # ----------------------------------------------------
        # Other errors
        # ----------------------------------------------------

        return (
            "Gemini could not complete the request.\n\n"
            f"Error: {error_text}"
        )

import json
import urllib.error
import urllib.request


# ============================================================
# LOCAL LLM CONFIGURATION
# ============================================================

OLLAMA_URL = "http://127.0.0.1:11434/api/chat"
MODEL_NAME = "qwen2.5-coder:3b"


# ============================================================
# AI DEBUGGING FUNCTION
# ============================================================

def get_ai_debugging_help(
    code,
    error_type="",
    error_message="",
    line="",
    language="Python"
):
    """
    Generate beginner-friendly debugging help using Ollama.

    Compatible with the existing DebugGenie function.
    Does not require a Gemini API key.
    """

 
    # --------------------------------------------------------
    # PROMPT
    # --------------------------------------------------------

    prompt = f"""
You are DebugGenie, an AI-powered programming debugger.

Selected programming language: {language}

Analyse the supplied source code and detected error information.

================ SOURCE CODE ================

{code}

================ ERROR INFORMATION ================

Error Type: {error_type or "Not specified"}
Error Message: {error_message or "Not specified"}
Error Line: {line or "Unknown"}

=============================================

Return your response using exactly these four headings:

1. What is the error?
Explain the actual error in beginner-friendly language.

2. Why did it happen?
Explain the specific cause based on the supplied source code.

3. How to fix it?
Explain the necessary changes briefly.

4. Corrected code
Provide the COMPLETE corrected version of the original source
code in the selected programming language.

STRICT RULES FOR CORRECTED CODE:
- Include the entire corrected program, not just the changed line.
- Preserve all original code that does not need changing.
- Fix the reported error and any directly related syntax issues.
- Do not replace the original program with a small example.
- Do not invent unrelated errors or make unrelated changes.
- Put the complete program inside one fenced code block.
- Use the appropriate code fence for {language}.
- Close the code block properly.
- Do not put explanations inside the corrected code block.
- If information is insufficient to safely correct the program,
  explain what is missing instead of inventing code.
- Do not omit code just to make the response shorter.

Keep the explanation concise, but make the corrected program complete.
"""


    # --------------------------------------------------------
    # OLLAMA REQUEST
    # --------------------------------------------------------

    payload = {
        "model": MODEL_NAME,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are DebugGenie, a careful programming "
                    "assistant. Explain errors accurately and "
                    "help beginners understand the solution."
                ),
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        "stream": False,
        "options": {
            "temperature": 0.2,
            "num_ctx": 4096,
            "num_predict": 800,
        },
    }

    request = urllib.request.Request(
        OLLAMA_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    # --------------------------------------------------------
    # SEND REQUEST
    # --------------------------------------------------------

    try:
        with urllib.request.urlopen(
            request,
            timeout=180
        ) as response:
            result = json.loads(
                response.read().decode("utf-8")
            )

        answer = (
            result.get("message", {})
            .get("content", "")
            .strip()
        )

        if answer:
            return answer

        return "The local LLM returned an empty response."

    # --------------------------------------------------------
    # ERROR HANDLING
    # --------------------------------------------------------

    except urllib.error.HTTPError as error:
        return (
            "The local LLM returned an HTTP error.\n\n"
            f"Status: {error.code}\n"
            "Check that Ollama is running and the model "
            "is available."
        )

    except (urllib.error.URLError, TimeoutError) as error:
        return (
            "DebugGenie could not connect to the local LLM.\n\n"
            "Please ensure Ollama is installed and running, "
            "and that the model is downloaded.\n\n"
            f"Details: {error}"
        )

    except (json.JSONDecodeError, TypeError, ValueError) as error:
        return (
            "DebugGenie could not process the local LLM response.\n\n"
            f"Details: {error}"
        )

    except Exception as error:
        return (
            "An unexpected local LLM error occurred.\n\n"
            f"Details: {error}"
        )

if __name__ == "__main__":
    result = get_ai_debugging_help(
        code='print("Hello"',
        error_type="SyntaxError",
        error_message="Missing closing parenthesis",
        line="1",
        language="Python",
    )
    print(result)

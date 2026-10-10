
import os
import re
import shutil
import subprocess
import tempfile


def check_javascript_code(code):
    """Check JavaScript syntax, including JavaScript transformer code."""

    node_path = shutil.which("node")

    if not node_path:
        possible_path = r"D:\Program Files\nodejs\node.exe"
        if os.path.isfile(possible_path):
            node_path = possible_path

    if not node_path:
        return {
            "success": False,
            "error_type": "RuntimeError",
            "error_line": None,
            "error_message": "Node.js was not found.",
            "suggestion": "Install Node.js and make sure node.exe is accessible."
        }

    # Extract inline JavaScript from an HTML document.
    if re.search(r"<!doctype\s+html|<html\b", code, re.I):
        scripts = re.findall(
            r"<script\b[^>]*>(.*?)</script\s*>",
            code,
            flags=re.I | re.S
        )

        if not scripts:
            return {
                "success": True,
                "error_type": None,
                "error_line": None,
                "error_message": "No inline JavaScript was found.",
                "suggestion": "HTML markup was not checked; no script blocks were available."
            }

        code_to_check = "\n;\n".join(scripts)
    else:
        code_to_check = code

    temp_path = None

    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".js",
            encoding="utf-8",
            newline="\n",
            delete=False
        ) as file:
            file.write(code_to_check)
            temp_path = file.name

        result = subprocess.run(
            [node_path, "--check", temp_path],
            capture_output=True,
            text=True,
            timeout=15,
            encoding="utf-8",
            errors="replace"
        )

        if result.returncode == 0:
            return {
                "success": True,
                "error_type": None,
                "error_line": None,
                "error_message": "No JavaScript syntax errors were found.",
                "suggestion": "JavaScript syntax is valid."
            }

        message = (result.stderr or result.stdout).strip()

        match = re.search(
            re.escape(temp_path) + r":(\d+)",
            message
        )
        line = int(match.group(1)) if match else None

        return {
            "success": False,
            "error_type": "SyntaxError",
            "error_line": line,
            "error_message": message,
            "suggestion": (
                f"Check the JavaScript syntax near line {line}."
                if line
                else "Review the JavaScript syntax and Node.js error message."
            )
        }

    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error_type": "TimeoutError",
            "error_line": None,
            "error_message": "JavaScript syntax checking timed out.",
            "suggestion": "Try checking the code again."
        }

    except Exception as error:
        return {
            "success": False,
            "error_type": "DebuggerError",
            "error_line": None,
            "error_message": str(error),
            "suggestion": "Check the Node.js installation."
        }

    finally:
        if temp_path and os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except OSError:
                pass

import subprocess
import tempfile
import os
import re


def check_cpp_code(code):
    """
    Check C++ code using G++.
    Compilation errors are detected without executing the program.
    """

    if not code or not code.strip():
        return {
            "success": False,
            "error_type": "EmptyCode",
            "error_message": "No C++ code was provided.",
            "error_line": None,
            "suggestion": "Enter some C++ code before starting the analysis."
        }

    temp_cpp = None
    temp_exe = None

    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".cpp",
            delete=False,
            encoding="utf-8"
        ) as file:

            file.write(code)
            temp_cpp = file.name

        temp_exe = temp_cpp[:-4] + ".exe"

        result = subprocess.run(
            [
                "g++",
                temp_cpp,
                "-o",
                temp_exe
            ],
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode == 0:
            return {
                "success": True,
                "error_type": None,
                "error_message": None,
                "error_line": None,
                "suggestion": "No C++ compilation errors were found."
            }

        error_message = result.stderr.strip()

        error_line = None

        match = re.search(
            r":(\d+):(?:\d+:)?\s*(?:error|warning):",
            error_message
        )

        if match:
            error_line = int(match.group(1))

        return {
            "success": False,
            "error_type": "CompilationError",
            "error_message": error_message,
            "error_line": error_line,
            "suggestion": "Check the compiler error near the reported line."
        }

    except FileNotFoundError:
        return {
            "success": False,
            "error_type": "CompilerNotFound",
            "error_message": "G++ compiler was not found.",
            "error_line": None,
            "suggestion": (
                "Make sure G++ is installed and available in PATH."
            )
        }

    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error_type": "CompilationTimeout",
            "error_message": "C++ compilation took too long and was stopped.",
            "error_line": None,
            "suggestion": "Check the C++ code and compiler configuration."
        }

    except Exception as e:
        return {
            "success": False,
            "error_type": "DebuggerError",
            "error_message": str(e),
            "error_line": None,
            "suggestion": "Check the C++ code and compiler installation."
        }

    finally:

        if temp_cpp and os.path.exists(temp_cpp):
            try:
                os.remove(temp_cpp)
            except OSError:
                pass

        if temp_exe and os.path.exists(temp_exe):
            try:
                os.remove(temp_exe)
            except OSError:
                pass
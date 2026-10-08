import subprocess
import tempfile
import os
import re


def check_c_code(code):
    """
    Check C code using GCC.
    This checks compilation errors only.
    The generated executable is NOT executed.
    """

    if not code or not code.strip():
        return {
            "success": False,
            "error_type": "EmptyCode",
            "error_message": "No C code was provided.",
            "error_line": None,
            "suggestion": "Enter some C code before starting the analysis."
        }

    temp_c = None
    temp_exe = None

    try:
        # Create temporary C source file
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".c",
            delete=False,
            encoding="utf-8"
        ) as file:

            file.write(code)
            temp_c = file.name

        # Create temporary executable path
        temp_exe = temp_c[:-2] + ".exe"

        # Compile C code
        result = subprocess.run(
            [
                "gcc",
                temp_c,
                "-o",
                temp_exe
            ],
            capture_output=True,
            text=True,
            timeout=30
        )

        # Compilation successful
        if result.returncode == 0:
            return {
                "success": True,
                "error_type": None,
                "error_message": None,
                "error_line": None,
                "suggestion": "No C compilation errors were found."
            }

        # Compilation failed
        error_message = result.stderr.strip()

        # Extract line number
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
            "error_message": "GCC compiler was not found.",
            "error_line": None,
            "suggestion": (
                "Make sure GCC is installed and available in PATH."
            )
        }

    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error_type": "CompilationTimeout",
            "error_message": "C compilation took too long and was stopped.",
            "error_line": None,
            "suggestion": "Check the C code and compiler configuration."
        }

    except Exception as e:
        return {
            "success": False,
            "error_type": "DebuggerError",
            "error_message": str(e),
            "error_line": None,
            "suggestion": "Check the C code and GCC installation."
        }

    finally:

        # Remove temporary C file
        if temp_c and os.path.exists(temp_c):
            try:
                os.remove(temp_c)
            except OSError:
                pass

        # Remove temporary executable
        if temp_exe and os.path.exists(temp_exe):
            try:
                os.remove(temp_exe)
            except OSError:
                pass
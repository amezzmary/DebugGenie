
import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path


def check_c_code(code):
    """Compile C code and return a normalized DebugGenie result."""

    if not code or not code.strip():
        return {
            "success": False,
            "error_type": "EmptyCode",
            "error_message": "No C code was provided.",
            "error_line": None,
            "suggestion": "Enter C code before starting the analysis."
        }

    compiler = shutil.which("gcc")

    # Support the MSYS2 UCRT64 compiler used on this project.
    if not compiler and os.path.isfile(r"D:\msys64\ucrt64\bin\gcc.exe"):
        compiler = r"D:\msys64\ucrt64\bin\gcc.exe"

    if not compiler:
        return {
            "success": False,
            "error_type": "CompilerNotFound",
            "error_message": "GCC was not found. Install or configure a C compiler.",
            "error_line": None,
            "suggestion": "Install GCC and add its bin folder to PATH."
        }

    try:
        with tempfile.TemporaryDirectory(prefix="debuggenie_c_") as folder:
            source = Path(folder) / "main.c"
            executable = Path(folder) / "main.exe"
            source.write_text(code, encoding="utf-8")

            result = subprocess.run(
                [compiler, "-fsyntax-only", str(source)],
                capture_output=True,
                text=True,
                timeout=15,
                errors="replace"
            )

            output = (result.stderr or result.stdout or "").strip()

            if result.returncode == 0:
                return {
                    "success": True,
                    "error_type": None,
                    "error_message": "No C compilation errors were found.",
                    "error_line": None,
                    "suggestion": "The C code passed compilation checks."
                }

            match = re.search(r":(\d+)(?::\d+)?:\s*(?:fatal )?error:", output)
            line = int(match.group(1)) if match else None

            return {
                "success": False,
                "error_type": "CompilationError",
                "error_message": output or "C compilation failed.",
                "error_line": line,
                "suggestion": (
                    "Check the reported line for missing semicolons, "
                    "braces, undeclared identifiers, or type errors."
                )
            }

    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error_type": "Timeout",
            "error_message": "C compilation took too long and was stopped.",
            "error_line": None,
            "suggestion": "Check your compiler installation and try again."
        }
    except (OSError, UnicodeError) as exc:
        return {
            "success": False,
            "error_type": "AnalysisError",
            "error_message": str(exc),
            "error_line": None,
            "suggestion": "Check the compiler configuration and source encoding."
        }
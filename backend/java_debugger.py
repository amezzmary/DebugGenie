
import re
import shutil
import subprocess
import tempfile
from pathlib import Path


def check_java_code(code):
    """Compile Java source code and return a DebugGenie result."""

    if not code or not code.strip():
        return {
            "success": False,
            "error_type": "EmptyCode",
            "error_message": "No Java code was provided.",
            "error_line": None,
            "suggestion": "Enter Java code before starting the analysis."
        }

    compiler = shutil.which("javac")

    if not compiler:
        return {
            "success": False,
            "error_type": "CompilerNotFound",
            "error_message": "Java compiler javac was not found.",
            "error_line": None,
            "suggestion": "Install a JDK and configure JAVA_HOME and PATH."
        }

    # Use the public class name when present; otherwise use Main.
    match = re.search(
        r"\bpublic\s+(?:final\s+)?class\s+([A-Za-z_$][\w$]*)",
        code
    )
    class_name = match.group(1) if match else "Main"

    try:
        with tempfile.TemporaryDirectory(prefix="debuggenie_java_") as folder:
            source = Path(folder) / f"{class_name}.java"
            source.write_text(code, encoding="utf-8")

            result = subprocess.run(
                [compiler, "-proc:none", "-XDrawDiagnostics", str(source)],
                capture_output=True,
                text=True,
                timeout=20,
                errors="replace",
                cwd=folder
            )

            output = (result.stderr or result.stdout or "").strip()

            if result.returncode == 0:
                return {
                    "success": True,
                    "error_type": None,
                    "error_message": "No Java compilation errors were found.",
                    "error_line": None,
                    "suggestion": "The Java code passed compilation checks."
                }

            line_match = re.search(r"\.java:(\d+):", output)
            if not line_match:
                line_match = re.search(r"\.java:(\d+)", output)

            return {
                "success": False,
                "error_type": "CompilationError",
                "error_message": output or "Java compilation failed.",
                "error_line": int(line_match.group(1)) if line_match else None,
                "suggestion": (
                    "Check the Java compiler message for missing punctuation, "
                    "type mismatches, undeclared variables, or class-name issues."
                )
            }

    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error_type": "Timeout",
            "error_message": "Java compilation took too long.",
            "error_line": None,
            "suggestion": "Check the JDK installation and retry."
        }
    except (OSError, UnicodeError) as exc:
        return {
            "success": False,
            "error_type": "AnalysisError",
            "error_message": str(exc),
            "error_line": None,
            "suggestion": "Check the Java compiler and source encoding."
        }
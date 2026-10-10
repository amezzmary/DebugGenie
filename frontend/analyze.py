```python
import streamlit as st
import sqlite3
from datetime import datetime

# ==========================================
# DATABASE
# ==========================================

DB_PATH = "debuggenie.db"


def save_analysis_to_history(code, result, language):
    """
    Save analysis result into analysis_history table.
    """

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        user_id = st.session_state.get("user_id")
        user_email = st.session_state.get("user_email", "")

        success = result.get("success", False)
        error_type = result.get("error_type")
        error_message = result.get("error_message")
        error_line = result.get("error_line")
        suggestion = result.get("suggestion")

        cursor.execute(
            """
            INSERT INTO analysis_history
            (
                user_id,
                user_email,
                file_name,
                language,
                code,
                success,
                error_type,
                error_message,
                error_line,
                suggestion,
                analyzed_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                user_id,
                user_email,
                "Pasted Code",
                language,
                code,
                1 if success else 0,
                error_type,
                error_message,
                error_line,
                suggestion,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            )
        )

        conn.commit()
        conn.close()

        return True, None

    except Exception as e:
        return False, str(e)


# ==========================================
# LANGUAGE DEBUGGER
# ==========================================

def analyze_code(code, language):
    """
    Select the correct debugger according to the
    programming language.
    """

    # ------------------------------------------
    # PYTHON
    # ------------------------------------------

    if language == "Python":

        from backend.debugger import check_python_code

        return check_python_code(code)

    # ------------------------------------------
    # C
    # ------------------------------------------

    elif language == "C":

        from backend.c_debugger import check_c_code

        return check_c_code(code)

    # ------------------------------------------
    # C++
    # ------------------------------------------

    elif language == "C++":

        from backend.cpp_debugger import check_cpp_code

        return check_cpp_code(code)

    # ------------------------------------------
    # JAVA
    # ------------------------------------------

    elif language == "Java":

        try:

            from backend.java_debugger import check_java_code

            return check_java_code(code)

        except ImportError:

            raise Exception(
                "Java debugger function "
                "'check_java_code' was not found."
            )

    # ------------------------------------------
    # JAVASCRIPT
    # ------------------------------------------

    elif language == "JavaScript":

        try:

            from backend.javascript_debugger import check_javascript_code

            return check_javascript_code(code)

        except ImportError:

            raise Exception(
                "JavaScript debugger function "
                "'check_javascript_code' was not found."
            )

    else:

        raise Exception(
            f"Unsupported programming language: {language}"
        )


# ==========================================
# ANALYZE PAGE
# ==========================================

def show_analyze():

    st.title("🧞 Debug Your Code")

    st.write(
        "Select a programming language, paste your code, "
        "and let DebugGenie analyze it for errors."
    )

    st.divider()

    # ==========================================
    # LANGUAGE SELECTION
    # ==========================================

    language = st.selectbox(
        "💻 Select Programming Language",
        [
            "Python",
            "C",
            "C++",
            "Java",
            "JavaScript"
        ]
    )

    # ==========================================
    # CODE PLACEHOLDER
    # ==========================================

    placeholders = {

        "Python": """Example:

x = 10
print(x)
""",

        "C": """Example:

#include <stdio.h>

int main() {
    int x = 10;
    printf("%d", x);
    return 0;
}
""",

        "C++": """Example:

#include <iostream>
using namespace std;

int main() {
    int x = 10;
    cout << x;
    return 0;
}
""",

        "Java": """Example:

public class Main {
    public static void main(String[] args) {
        int x = 10;
        System.out.println(x);
    }
}
""",

        "JavaScript": """Example:

let x = 10;
console.log(x);
"""
    }

    # ==========================================
    # CODE INPUT
    # ==========================================

    code = st.text_area(
        f"{language} Code",
        height=350,
        placeholder=placeholders[language]
    )

    st.write("")

    col1, col2 = st.columns(2)

    # ==========================================
    # ANALYZE BUTTON
    # ==========================================

    with col1:

        if st.button(
            "🔍 Analyze Code",
            use_container_width=True
        ):

            if not code.strip():

                st.warning(
                    f"Please enter some {language} code first."
                )

            else:

                try:

                    # ==================================
                    # RUN CORRECT DEBUGGER
                    # ==================================

                    result = analyze_code(
                        code,
                        language
                    )

                    # ==================================
                    # MAKE SURE RESULT IS A DICTIONARY
                    # ==================================

                    if not isinstance(result, dict):

                        result = {
                            "success": False,
                            "error_type": "DebuggerError",
                            "error_message": str(result),
                            "error_line": None,
                            "suggestion": (
                                "The debugger returned an "
                                "unexpected result."
                            )
                        }

                    # ==================================
                    # SAVE RESULT IN SESSION
                    # ==================================

                    st.session_state.analysis_result = result
                    st.session_state.analysis_code = code
                    st.session_state.analysis_language = language

                    # ==================================
                    # SAVE RESULT TO DATABASE
                    # ==================================

                    saved, error = save_analysis_to_history(
                        code,
                        result,
                        language
                    )

                    if not saved:

                        st.warning(
                            f"Analysis completed, but history "
                            f"could not be saved: {error}"
                        )

                    # ==================================
                    # GO TO RESULTS
                    # ==================================

                    st.session_state.page = "results"

                    st.rerun()

                except Exception as e:

                    st.error(
                        f"Analysis error: {e}"
                    )
```

import streamlit as st
import sqlite3
from datetime import datetime
from backend.c_debugger import check_c_code
from backend.cpp_debugger import check_cpp_code


# ============================================================
# BACKEND IMPORTS
# ============================================================

from backend.debugger import check_python_code
from backend.gemini_debugger import get_ai_debugging_help

from backend.database import login_user, register_user


# ============================================================
# FRONTEND IMPORTS
# ============================================================

from frontend.styles import load_styles

from frontend.components import (
    render_footer,
    render_file_information,
    render_success_result,
    render_error_result,
    render_ai_analysis,
    render_submitted_code,
    render_empty_state,
    render_user_history_item,
    render_admin_history_item,
)

from frontend.pages import (
    render_home_header,
    render_home_hero,
    render_home_features,
    render_login_page_title,
    render_register_page_title,
    render_dashboard_stats,
    render_admin_stats,
    render_login_header,
    render_register_header,
    render_dashboard_page_title,
    render_analyze_page_title,
    render_results_page_title,
    render_history_page_title,
    render_admin_page_title,
    render_admin_users_page_title,
    render_admin_history_page_title,
)


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="DebugGenie",
    page_icon="🐞",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ============================================================
# DATABASE
# ============================================================

DB = "debuggenie.db"


# ============================================================
# SESSION STATE
# ============================================================

defaults = {
    "page": "home",
    "logged_in": False,
    "user_id": None,
    "username": None,
    "user_email": None,
    "user_role": None,

    # Latest analysis
    "analysis_result": None,
    "analysis_code": "",
    "analysis_filename": "",
    "analysis_language": "Python",
    "analysis_suggestion": "",
    "ai_debugging_help": "",
}


for key, value in defaults.items():

    if key not in st.session_state:
        st.session_state[key] = value


# ============================================================
# HISTORY DATABASE INITIALIZATION
# ============================================================

def init_history():

    conn = sqlite3.connect(DB)
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS analysis_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            user_email TEXT,
            file_name TEXT,
            language TEXT NOT NULL,
            code TEXT NOT NULL,
            success INTEGER NOT NULL,
            error_type TEXT,
            error_message TEXT,
            error_line TEXT,
            suggestion TEXT,
            analyzed_at TEXT
        )
        """
    )

    # --------------------------------------------------------
    # Check existing columns
    # --------------------------------------------------------

    cursor.execute(
        "PRAGMA table_info(analysis_history)"
    )

    columns = [
        row[1]
        for row in cursor.fetchall()
    ]

    required_columns = {
        "user_email": "TEXT",
        "file_name": "TEXT",
        "error_message": "TEXT",
        "error_line": "TEXT",
        "suggestion": "TEXT",
        "analyzed_at": "TEXT",
    }

    for column, data_type in required_columns.items():

        if column not in columns:

            try:

                cursor.execute(
                    f"""
                    ALTER TABLE analysis_history
                    ADD COLUMN {column} {data_type}
                    """
                )

            except sqlite3.OperationalError:
                pass

    conn.commit()
    conn.close()


# ============================================================
# SAVE HISTORY
# ============================================================

def save_history(
    result,
    code,
    file_name,
    language,
    suggestion,
):

    if not st.session_state.logged_in:
        return

    conn = sqlite3.connect(DB)

    cursor = conn.cursor()

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
            st.session_state.user_id,
            st.session_state.user_email,
            file_name,
            language,
            code,
            1 if result.get("success") else 0,
            result.get("error_type", ""),
            result.get("message", ""),
            str(result.get("line", "")),
            suggestion,
            datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
        ),
    )

    conn.commit()
    conn.close()


# ============================================================
# USER HISTORY
# ============================================================

def user_history():

    conn = sqlite3.connect(DB)

    rows = conn.execute(
        """
        SELECT
            id,
            file_name,
            language,
            success,
            error_type,
            error_message,
            error_line,
            suggestion,
            analyzed_at
        FROM analysis_history
        WHERE user_id = ?
        ORDER BY id DESC
        """,
        (
            st.session_state.user_id,
        ),
    ).fetchall()

    conn.close()

    return rows


# ============================================================
# ALL HISTORY
# ============================================================

def all_history():

    conn = sqlite3.connect(DB)

    rows = conn.execute(
        """
        SELECT
            id,
            user_email,
            file_name,
            language,
            success,
            error_type,
            error_message,
            error_line,
            analyzed_at
        FROM analysis_history
        ORDER BY id DESC
        """
    ).fetchall()

    conn.close()

    return rows


# ============================================================
# USER STATISTICS
# ============================================================

def stats_for_user():

    conn = sqlite3.connect(DB)

    total = conn.execute(
        """
        SELECT COUNT(*)
        FROM analysis_history
        WHERE user_id = ?
        """,
        (
            st.session_state.user_id,
        ),
    ).fetchone()[0]

    errors = conn.execute(
        """
        SELECT COUNT(*)
        FROM analysis_history
        WHERE user_id = ?
        AND success = 0
        """,
        (
            st.session_state.user_id,
        ),
    ).fetchone()[0]

    conn.close()

    return total, errors


# ============================================================
# ADMIN STATISTICS
# ============================================================

def stats_all():

    conn = sqlite3.connect(DB)

    users = conn.execute(
        "SELECT COUNT(*) FROM users"
    ).fetchone()[0]

    analyses = conn.execute(
        "SELECT COUNT(*) FROM analysis_history"
    ).fetchone()[0]

    errors = conn.execute(
        """
        SELECT COUNT(*)
        FROM analysis_history
        WHERE success = 0
        """
    ).fetchone()[0]

    conn.close()

    return users, analyses, errors


# ============================================================
# INITIALIZE DATABASE
# ============================================================

init_history()


# ============================================================
# LOAD EXISTING DESIGN
# ============================================================

load_styles()


# ============================================================
# HOME PAGE
# ============================================================

def home():

    # --------------------------------------------------------
    # HOME HEADER
    # --------------------------------------------------------

    render_home_header()

    # --------------------------------------------------------
    # HERO
    # --------------------------------------------------------

    render_home_hero()

    # --------------------------------------------------------
    # ANALYZE CODE BUTTON
    # --------------------------------------------------------

    st.write("")

    col1, col2, col3 = st.columns([1, 1.2, 1])

    with col2:

        if st.button(
            "📤 Analyze Code",
            use_container_width=True,
            key="home_analyze"
        ):

            # User must login/signup before analyzing
            if st.session_state.logged_in:

                st.session_state.page = "analyze"

            else:

                st.session_state.page = "login"

            st.rerun()

    # --------------------------------------------------------
    # FEATURES
    # --------------------------------------------------------

    render_home_features()


    # ========================================================
    # HOME CONTENT
    # ========================================================

    render_home_hero()

    render_home_features()


# ============================================================
# LOGIN PAGE
# ============================================================

def login_page():

    _, col, _ = st.columns(
        [1, 1.2, 1]
    )

    with col:

        render_login_page_title()

        email = st.text_input(
            "📧 Email",
            key="login_email",
        )

        password = st.text_input(
            "🔒 Password",
            type="password",
            key="login_password",
        )

        if st.button(
            "🔐 Login",
            key="login_btn",
        ):

            if not email or not password:

                st.error(
                    "Please enter your email and password."
                )

            else:

                try:

                    result = login_user(
                        email.strip(),
                        password,
                    )

                    if result["success"]:

                        st.session_state.logged_in = True

                        st.session_state.user_id = result["id"]

                        st.session_state.username = result["name"]

                        st.session_state.user_email = result["email"]

                        st.session_state.user_role = result["role"]

                        if result["role"] == "admin":
                            st.session_state.page = "admin"
                        else:
                            st.session_state.page = "dashboard"

                        st.rerun()

                    else:

                        st.error(
                            result["message"]
                        )

                except Exception as ex:

                    st.error(
                        f"Login error: {ex}"
                    )

        if st.button(
            "📝 Create New Account",
            key="new_account",
        ):

            st.session_state.page = "register"

            st.rerun()

        if st.button(
            "← Back to Home",
            key="login_home",
        ):

            st.session_state.page = "home"

            st.rerun()


# ============================================================
# REGISTER PAGE
# ============================================================

def register_page():

    _, col, _ = st.columns(
        [1, 1.2, 1]
    )

    with col:

        render_register_page_title()

        name = st.text_input(
            "👤 Full Name",
            key="reg_name",
        )

        email = st.text_input(
            "📧 Email",
            key="reg_email",
        )

        password = st.text_input(
            "🔒 Password",
            type="password",
            key="reg_pass",
        )

        confirm_password = st.text_input(
            "🔒 Confirm Password",
            type="password",
            key="reg_confirm",
        )

        if st.button(
            "📝 Create Account",
            key="reg_btn",
        ):

            if not name or not email or not password:

                st.error(
                    "Please fill in all fields."
                )

            elif password != confirm_password:

                st.error(
                    "Passwords do not match."
                )

            elif len(password) < 6:

                st.error(
                    "Password must contain at least 6 characters."
                )

            elif "@" not in email or "." not in email:

                st.error(
                    "Enter a valid email address."
                )

            else:

                try:

                    result = register_user(
                        name.strip(),
                        email.strip(),
                        password,
                    )

                    if result["success"]:

                        st.success(
                            "✅ Account created successfully!"
                        )

                        st.session_state.page = "login"

                    else:

                        st.error(
                            result["message"]
                        )

                except Exception as ex:

                    st.error(
                        f"Registration error: {ex}"
                    )

        if st.button(
            "← Back to Login",
            key="reg_back",
        ):

            st.session_state.page = "login"

            st.rerun()


# ============================================================
# USER DASHBOARD
# ============================================================

def dashboard():

    render_dashboard_page_title()

    total, errors = stats_for_user()

    successful = total - errors

    render_dashboard_stats(
        total,
        successful,
        errors
    )

    st.write("")

    col1, col2 = st.columns(2)

    with col1:

        if st.button(
            "📤 Upload / Analyze Code",
            key="dash_analyze"
        ):

            st.session_state.page = "analyze"
            st.rerun()

    with col2:

        if st.button(
            "🕘 Analysis History",
            key="dash_history"
        ):

            st.session_state.page = "history"
            st.rerun()

# ============================================================
# ANALYZE CODE
# ============================================================

def analyze_page():

    render_analyze_page_title()

    method = st.radio(
        "Choose input method:",
        [
            "Paste Code",
            "Upload Python File",
        ],
        horizontal=True,
        key="input_method",
    )

    code = ""

    filename = "Pasted Code"
    

    # --------------------------------------------------------
    # PASTE CODE
    # --------------------------------------------------------

    if method == "Paste Code":

        code = st.text_area(
            "💻 Your Python Code",
            height=350,
            placeholder=(
                "Example:\n\n"
                "x = 10\n"
                "print(y)"
            ),
            key="editor",
        )

    # --------------------------------------------------------
    # UPLOAD FILE
    # --------------------------------------------------------

    else:

        uploaded_file = st.file_uploader(
            "📤 Upload Programming File",
            type=["py"],
            key="upload",
        )

        if uploaded_file:

            filename = uploaded_file.name

            try:

                code = uploaded_file.read().decode(
                    "utf-8"
                )

                st.success(
                    f"✅ {filename} uploaded successfully."
                )

                st.subheader(
                    "📄 Uploaded Code"
                )

                st.code(
                    code,
                    language="python",
                )

            except UnicodeDecodeError:

                st.error(
                    "Unable to read the file. "
                    "Please use a UTF-8 encoded Python file."
                )

    # --------------------------------------------------------
    # LANGUAGE
    # --------------------------------------------------------

    language = st.selectbox(
    "Programming Language",
    [
        "Python",
        "C",
        "C++",
        "Java",
        "JavaScript"
    ]
    )  
    # --------------------------------------------------------
    # START ANALYSIS
    # --------------------------------------------------------

    if st.button(
        "🔍 Start Analysis",
        key="analyze_btn",
    ):

        if not code.strip():

            st.warning(
                "Please enter or upload code first."
            )

            return

        # ----------------------------------------------------
        # LOCAL DEBUGGER
        # ----------------------------------------------------

        with st.spinner(
            "🔍 DebugGenie is checking your code..."
        ):

            
            try:
                if language == "Python":
                    result = check_python_code(code)

                elif language == "C":
                    from backend.c_debugger import check_c_code
                    result = check_c_code(code)

                elif language == "C++":
                    from backend.cpp_debugger import check_cpp_code
                    result = check_cpp_code(code)

                elif language == "Java":
                    from backend.java_debugger import check_java_code
                    result = check_java_code(code)

                elif language == "JavaScript":
                    from backend.javascript_debugger import check_javascript_code
                    result = check_javascript_code(code)

                else:
                    st.error("Unsupported programming language.")
                    return

            except Exception as ex:
                st.error(f"Debugger error: {ex}")
                return

        # ----------------------------------------------------
        # GEMINI AI
        # ----------------------------------------------------

        with st.spinner(
            "🤖 DebugGenie AI is generating your solution..."
        ):

            try:

                ai_help = get_ai_debugging_help(
                    code=code,
                    error_type=result.get(
                        "error_type",
                        "",
                    ),
                    error_message=result.get(
                        "message",
                        "",
                    ),
                    line=str(
                        result.get(
                            "line",
                            "",
                        )
                    ),
                )

            except Exception as ex:

                ai_help = (
                    "Gemini AI Error:\n\n"
                    f"{ex}"
                )

        # ----------------------------------------------------
        # SAVE ANALYSIS
        # ----------------------------------------------------

        st.session_state.analysis_result = result

        st.session_state.analysis_code = code

        st.session_state.analysis_filename = filename

        st.session_state.analysis_language = language

        st.session_state.ai_debugging_help = ai_help

        # ----------------------------------------------------
        # LOCAL SUGGESTION
        # ----------------------------------------------------

        if result.get("success"):

            suggestion = (
                "No syntax or undefined-variable errors "
                "were detected. Review code quality, "
                "readability, and maintainability."
            )

        else:

            error_type = result.get(
                "error_type",
                "Unknown Error",
            )

            if error_type == "SyntaxError":

                suggestion = (
                    "Check for missing colons, brackets, "
                    "parentheses, commas, quotation marks, "
                    "or incorrect indentation."
                )

            elif error_type == "UndefinedVariable":

                suggestion = (
                    "The variable is being used before it "
                    "has been defined. Check the variable "
                    "name and define it before using it."
                )

            elif error_type == "IndentationError":

                suggestion = (
                    "Check the indentation around the "
                    "reported line."
                )

            else:

                suggestion = (
                    "Review the reported line and the "
                    "error message carefully."
                )

        st.session_state.analysis_suggestion = suggestion

        # ----------------------------------------------------
        # SAVE HISTORY
        # ----------------------------------------------------

        try:

            save_history(
                result,
                code,
                filename,
                language,
                suggestion,
            )

        except Exception as ex:

            st.warning(
                "Analysis completed, but history "
                f"could not be saved: {ex}"
            )

        # ----------------------------------------------------
        # SHOW RESULTS
        # ----------------------------------------------------

        st.session_state.page = "results"

        st.rerun()


# ============================================================
# RESULTS PAGE
# ============================================================

def results_page():

    render_results_page_title()

    result = st.session_state.get(
        "analysis_result"
    )

    if not result:

        render_empty_state(
            "No analysis result available.",
            "🐞",
        )

        if st.button(
            "📤 Analyze Code",
            key="no_result_analyze",
        ):

            st.session_state.page = "analyze"

            st.rerun()

        return

    # --------------------------------------------------------
    # GET DATA
    # --------------------------------------------------------

    code = st.session_state.get(
        "analysis_code",
        "",
    )

    filename = st.session_state.get(
        "analysis_filename",
        "Pasted Code",
    )

    language = st.session_state.get(
        "analysis_language",
        "Python",
    )

    suggestion = st.session_state.get(
        "analysis_suggestion",
        "",
    )

    ai_help = st.session_state.get(
        "ai_debugging_help",
        "",
    )

    # --------------------------------------------------------
    # FILE INFORMATION
    # --------------------------------------------------------

    render_file_information(
        filename,
        language,
    )

    st.divider()

    # --------------------------------------------------------
    # SUCCESS
    # --------------------------------------------------------

    if result.get("success"):

        render_success_result(
            result.get(
                "message",
                "No errors detected.",
            )
        )

    # --------------------------------------------------------
    # ERROR
    # --------------------------------------------------------

    else:

        render_error_result(
            error_type=result.get(
                "error_type",
                "Unknown Error",
            ),
            line=result.get(
                "line",
                "Unknown",
            ),
            message=result.get(
                "message",
                "An error was detected.",
            ),
            code=code,
            suggestion=suggestion,
        )

    # --------------------------------------------------------
    # GEMINI
    # --------------------------------------------------------

    st.divider()

    render_ai_analysis(
        ai_help
    )

    # --------------------------------------------------------
    # SUBMITTED CODE
    # --------------------------------------------------------

    st.divider()

    render_submitted_code(
        code
    )

    # --------------------------------------------------------
    # DOWNLOAD REPORT
    # --------------------------------------------------------

    st.divider()

    st.subheader(
        "📄 Debugging Report"
    )

    report_lines = []

    report_lines.append(
        "DEBUGGENIE - DEBUGGING REPORT"
    )

    report_lines.append(
        "=" * 50
    )

    report_lines.append("")

    report_lines.append(
        f"File: {filename}"
    )

    report_lines.append(
        f"Language: {language}"
    )

    report_lines.append("")

    # Status

    if result.get("success"):

        report_lines.append(
            "STATUS: No basic errors detected."
        )

    else:

        report_lines.append(
            "STATUS: Error detected"
        )

        report_lines.append(
            f"Error Type: {result.get('error_type', 'Unknown')}"
        )

        report_lines.append(
            f"Line: {result.get('line', 'Unknown')}"
        )

        report_lines.append(
            f"Error Message: {result.get('message', '')}"
        )

    # Suggestion

    report_lines.append("")

    report_lines.append(
        "SUGGESTION"
    )

    report_lines.append(
        "-" * 50
    )

    report_lines.append(
        suggestion or "No suggestion available."
    )

    # AI

    report_lines.append("")

    report_lines.append(
        "AI DEBUGGING ANALYSIS"
    )

    report_lines.append(
        "-" * 50
    )

    report_lines.append(
        ai_help or "AI analysis not available."
    )

    # Code

    report_lines.append("")

    report_lines.append(
        "SUBMITTED CODE"
    )

    report_lines.append(
        "-" * 50
    )

    report_lines.append(
        code
    )

    report_lines.append("")

    report_lines.append(
        "=" * 50
    )

    report_lines.append(
        "Generated by DebugGenie"
    )

    report_text = "\n".join(
        report_lines
    )

    st.download_button(
        label="📥 Download Debugging Report",
        data=report_text,
        file_name="debuggenie_report.txt",
        mime="text/plain",
        key="download_debug_report",
    )

    # --------------------------------------------------------
    # NAVIGATION
    # --------------------------------------------------------

    st.divider()

    col1, col2, col3 = st.columns(3)

    with col1:

        if st.button(
            "📤 Analyze Another Program",
            key="another_analysis",
        ):

            st.session_state.page = "analyze"

            st.rerun()

    with col2:

        if st.button(
            "🕘 View History",
            key="result_history",
        ):

            st.session_state.page = "history"

            st.rerun()

    with col3:

        if st.button(
            "📊 Dashboard",
            key="result_dashboard",
        ):

            st.session_state.page = "dashboard"

            st.rerun()


# ============================================================
# USER HISTORY PAGE
# ============================================================

def history_page():

    render_history_page_title()

    rows = user_history()

    if not rows:

        render_empty_state(
            "No analysis history yet.",
            "Analyze some code and it will appear here."
        )

        return

    for row in rows:

        (
            history_id,
            filename,
            language,
            success,
            error_type,
            error_message,
            error_line,
            suggestion,
            analyzed_at,
        ) = row

        # Convert database row into the dictionary
        # expected by render_user_history_item()

        item = {
            "id": history_id,
            "file_name": filename,
            "language": language,
            "success": bool(success),
            "error_type": error_type,
            "error_message": error_message,
            "error_line": error_line,
            "suggestion": suggestion,
            "analyzed_at": analyzed_at,
        }

        render_user_history_item(item)
# ============================================================
# ADMIN DASHBOARD
# ============================================================

def admin_page():

    render_admin_page_title()

    users, analyses, errors = stats_all()

    render_admin_stats(
        users,
        analyses,
        errors,
    )

    st.write("")

    if st.button(
        "👥 User Management",
        key="admin_users",
    ):

        st.session_state.page = "admin_users"

        st.rerun()

    if st.button(
        "📈 All Analysis History",
        key="admin_history",
    ):

        st.session_state.page = "admin_history"

        st.rerun()


# ============================================================
# ADMIN USER MANAGEMENT
# ============================================================

def admin_users():

    render_admin_users_page_title()

    conn = sqlite3.connect(DB)

    rows = conn.execute(
        """
        SELECT
            id,
            name,
            email,
            role,
            created_at
        FROM users
        ORDER BY id DESC
        """
    ).fetchall()

    conn.close()

    st.dataframe(
        rows,
        column_config={
            0: "ID",
            1: "Name",
            2: "Email",
            3: "Role",
            4: "Created At",
        },
        use_container_width=True,
        hide_index=True,
    )


# ============================================================
# ADMIN HISTORY
# ============================================================

def admin_history():

    render_admin_history_page_title()

    rows = all_history()

    if not rows:

        render_empty_state(
            "No analyses recorded yet.",
            "Analysis activity will appear here."
        )

        return

    for row in rows:

        (
            history_id,
            email,
            filename,
            language,
            success,
            error_type,
            error_message,
            error_line,
            analyzed_at,
        ) = row

        # Convert database row into the dictionary
        # expected by render_admin_history_item()

        item = {
            "id": history_id,
            "user_email": email,
            "file_name": filename,
            "language": language,
            "success": bool(success),
            "error_type": error_type,
            "error_message": error_message,
            "error_line": error_line,
            "analyzed_at": analyzed_at,
        }

        render_admin_history_item(item)

# ============================================================
# LOGOUT
# ============================================================

def logout():

    st.session_state.logged_in = False

    st.session_state.user_id = None

    st.session_state.username = None

    st.session_state.user_email = None

    st.session_state.user_role = None

    st.session_state.analysis_result = None

    st.session_state.analysis_code = ""

    st.session_state.analysis_filename = ""

    st.session_state.analysis_language = "Python"

    st.session_state.analysis_suggestion = ""

    st.session_state.ai_debugging_help = ""

    st.session_state.page = "home"

    st.rerun()


# ============================================================
# SIDEBAR
# ============================================================

if st.session_state.logged_in:

    with st.sidebar:

        st.title("🧞 DebugGenie")

        st.caption(
            f"Logged in as: "
            f"{st.session_state.username}"
        )

        st.divider()

        # ----------------------------------------------------
        # NORMAL USER
        # ----------------------------------------------------

        if st.session_state.user_role == "user":

            if st.button(
                "📊 Dashboard",
                key="side_dash",
            ):

                st.session_state.page = "dashboard"

                st.rerun()

            if st.button(
                "📤 Analyze Code",
                key="side_analyze",
            ):

                st.session_state.page = "analyze"

                st.rerun()

            if st.button(
                "🐞 Latest Result",
                key="side_results",
            ):

                if st.session_state.analysis_result:

                    st.session_state.page = "results"

                    st.rerun()

                else:

                    st.info(
                        "No analysis result available yet."
                    )

            if st.button(
                "🕘 History",
                key="side_history",
            ):

                st.session_state.page = "history"

                st.rerun()

        # ----------------------------------------------------
        # ADMIN
        # ----------------------------------------------------

        else:

            if st.button(
                "🛡️ Admin Dashboard",
                key="side_admin",
            ):

                st.session_state.page = "admin"

                st.rerun()

            if st.button(
                "👥 User Management",
                key="side_users",
            ):

                st.session_state.page = "admin_users"

                st.rerun()

            if st.button(
                "📈 Analysis History",
                key="side_admin_history",
            ):

                st.session_state.page = "admin_history"

                st.rerun()

        st.divider()

        if st.button(
            "🏠 Home",
            key="side_home",
        ):

            st.session_state.page = "home"

            st.rerun()

        if st.button(
            "🚪 Logout",
            key="side_logout",
        ):

            logout()


# ============================================================
# ROUTING
# ============================================================

page = st.session_state.page


if page == "home":

    home()


elif page == "login":

    login_page()


elif page == "register":

    register_page()


elif (
    page == "dashboard"
    and st.session_state.logged_in
):

    dashboard()


elif (
    page == "analyze"
    and st.session_state.logged_in
):

    analyze_page()


elif (
    page == "results"
    and st.session_state.logged_in
):

    results_page()


elif (
    page == "history"
    and st.session_state.logged_in
):

    history_page()


elif (
    page == "admin"
    and st.session_state.logged_in
    and st.session_state.user_role == "admin"
):

    admin_page()


elif (
    page == "admin_users"
    and st.session_state.logged_in
    and st.session_state.user_role == "admin"
):

    admin_users()


elif (
    page == "admin_history"
    and st.session_state.logged_in
    and st.session_state.user_role == "admin"
):

    admin_history()


else:

    st.session_state.page = "home"

    st.rerun()


# ============================================================
# FOOTER
# ============================================================

render_footer()
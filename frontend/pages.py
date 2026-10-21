import streamlit as st
import streamlit as st
import streamlit.components.v1 as components


# ============================================================
# HOME
# ============================================================

from pathlib import Path
import streamlit as st

import streamlit as st


import base64
from pathlib import Path
import streamlit as st


def render_home_header():
    # Adjust path if your image location differs
    img_path = Path("assets/genie_lamp.png")

    if img_path.exists():
        encoded_img = base64.b64encode(img_path.read_bytes()).decode("utf-8")

        st.markdown(
            f"""
            <div style="
                display: flex; 
                align-items: center; 
                justify-content: center; 
                gap: 12px; 
                white-space: nowrap;
                width: 100%;
                margin-bottom: 30px;
            ">
                <img src="data:image/png;base64,{encoded_img}" style="height: 51px; width: auto; flex-shrink: 0;" />
                <h1 style="
                    margin: 0; 
                    padding: 0; 
                    font-size: 3.2rem; 
                    font-weight: 700; 
                    color: #1e1b4b; 
                    line-height: 1;
                    display: inline;
                ">DebugGenie</h1>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.error(f"Image not found at {img_path.resolve()}")
def render_home_hero():

    components.html(
        """
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {
                    margin: 0;
                    padding: 20px 10px;
                    background: transparent;
                    font-family: Arial, sans-serif;
                    text-align: center;
                }

                .badge {
                    display: inline-block;
                    padding: 8px 18px;
                    border-radius: 25px;
                    background: #f0e9ff;
                    color: #7048b8;
                    font-size: 13px;
                    font-weight: 700;
                    margin-bottom: 18px;
                }

                h1 {
                    font-size: 48px;
                    line-height: 1.15;
                    margin: 0 0 15px 0;
                    color: #222;
                }

                h1 span {
                    color: #7048b8;
                }

                p {
                    font-size: 18px;
                    color: #666;
                    margin: 0;
                }
            </style>
        </head>

        <body>

            <div class="badge">
                ✨ POWERED BY LLM INTELLIGENCE
            </div>

            <h1>
                Your AI Pair Programmer<br>
                for <span>Smarter Debugging</span>
            </h1>

            <p>
                Find bugs • Understand errors •
                Get AI-powered debugging assistance
            </p>

        </body>
        </html>
        """,
        height=230,
        scrolling=False
    )

def render_home_features():
    st.markdown("## ✨  Features")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("###  Multi-Language")
        st.write(
            "Analyze your Python programs and "
            "identify common coding errors."
        )

    with col2:
        st.markdown("### 🔍 Deep Analysis")
        st.write(
            "Detect syntax errors and "
            "undefined variables."
        )

    with col3:
        st.markdown("### 🤖 LLM Insights")
        st.write(
            "Get beginner-friendly explanations "
            "and debugging suggestions."
        )

    col4, col5, col6 = st.columns(3)

    with col4:
        st.markdown("### 📄 Reports")
        st.write(
            "Generate and download debugging reports."
        )

    with col5:
        st.markdown("### 🕘 History")
        st.write(
            "Keep track of your previous code analyses."
        )

    with col6:
        st.markdown("### 🔐 Secure")
        st.write(
            "Your account and analysis history "
            "are protected."
        )


# ============================================================
# LOGIN
# ============================================================

def render_login_header():
    st.markdown("## 🔐 Welcome Back")


# ============================================================
# REGISTER
# ============================================================

def render_register_header():
    st.markdown("## ✨ Create Your DebugGenie Account")


# ============================================================
# DASHBOARD
# ============================================================

def render_dashboard_stats(
    total,
    successful,
    errors
):
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Total Analyses",
            total
        )

    with col2:
        st.metric(
            "Successful",
            successful
        )

    with col3:
        st.metric(
            "Errors Found",
            errors
        )


def render_admin_stats(
    total_users,
    total_analyses,
    total_errors
):
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Total Users",
            total_users
        )

    with col2:
        st.metric(
            "Total Analyses",
            total_analyses
        )

    with col3:
        st.metric(
            "Errors Found",
            total_errors
        )


# ============================================================
# PAGE TITLES
# ============================================================

def render_login_page_title():
    st.title("🔐 Login")
    st.write(
        "Login to continue using DebugGenie."
    )


def render_register_page_title():
    st.title("✨ Create Account")
    st.write(
        "Create your DebugGenie account."
    )


def render_dashboard_page_title():
    st.title("📊 Dashboard")
    st.write(
        "Welcome to your DebugGenie dashboard."
    )


def render_analyze_page_title():
    st.title("🐞 Debug Your Code")
    st.write(
        "Paste your Python code or upload a "
        "Python file and let DebugGenie analyze it."
    )


def render_results_page_title():
    st.title("📋 Debugging Results")
    st.write(
        "Review your debugging analysis and "
        "AI-powered suggestions."
    )


def render_history_page_title():
    st.title("🕘 Analysis History")
    st.write(
        "View your previous debugging analyses."
    )


def render_admin_page_title():
    st.title("⚙️ Admin Dashboard")
    st.write(
        "Manage users and monitor DebugGenie analyses."
    )


def render_admin_users_page_title():
    st.title("👥 Users")
    st.write(
        "View registered DebugGenie users."
    )


def render_admin_history_page_title():
    st.title("📚 All Analysis History")
    st.write(
        "View analysis activity from all users."
    )
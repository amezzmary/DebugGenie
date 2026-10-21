import streamlit as st


def load_styles():
    st.markdown(
        """
        <style>

        /* Main background */
        .stApp {
            background-color: #F3E8FF !important;
        }

        /* Target all Streamlit text & markdown containers */
        [data-testid="stMarkdownContainer"] p,
        [data-testid="stMarkdownContainer"] span,
        [data-testid="stMarkdownContainer"] li,
        label {
            color: #2D064E !important; /* Deep Eggplant / Dark Purple */
        }

        /* Headings - Distinct Purple Tones */
        [data-testid="stMarkdownContainer"] h1 {
            color: #3B0764 !important; /* Rich Dark Purple */
            font-weight: 800 !important;
        }

        [data-testid="stMarkdownContainer"] h2,
        [data-testid="stMarkdownContainer"] h3 {
            color: #581C87 !important; /* Deep Royal Purple */
            font-weight: 700 !important;
        }

        /* Muted / Subtitle text */
        .muted-text {
            color: #7E22CE !important;
            font-weight: 600;
        }

        /* Buttons styling */
        .stButton > button {
            background-color: #9333EA !important;
            color: #FFFFFF !important;
            border-radius: 10px !important;
            border: none !important;
            font-weight: 600 !important;
        }

        .stButton > button:hover {
            background-color: #7E22CE !important;
            color: #FFFFFF !important;
        }

        /* Sidebar styling */
        section[data-testid="stSidebar"] {
            background-color: #FAF9FF !important;
        }

        section[data-testid="stSidebar"] * {
            color: #3B0764 !important;
        }

        </style>
        """,
        unsafe_allow_html=True
    )
import streamlit as st


def load_styles():
    st.markdown(
        """
        <style>

        /* Main background */
        .stApp {
            background: linear-gradient(
                135deg,
                #f8f7ff 0%,
                #ffffff 50%,
                #f3efff 100%
            );
        }

        /* Main content */
        .main {
            padding-top: 1rem;
        }

        /* Buttons */
        .stButton > button {
            border-radius: 10px;
            font-weight: 600;
            border: none;
            padding: 0.55rem 1.2rem;
            transition: 0.2s;
        }

        .stButton > button:hover {
            transform: translateY(-1px);
        }

        /* Text inputs */
        .stTextInput input,
        .stTextArea textarea {
            border-radius: 10px;
        }

        /* File uploader */
        [data-testid="stFileUploader"] {
            border-radius: 12px;
        }

        /* Cards */
        .debug-card {
            background: white;
            padding: 25px;
            border-radius: 18px;
            box-shadow: 0 4px 18px rgba(80, 60, 120, 0.08);
            margin-bottom: 20px;
        }

        /* Headings */
        h1, h2, h3 {
            font-weight: 700;
        }

        /* Sidebar */
        section[data-testid="stSidebar"] {
            background: #faf9ff;
        }

        /* Code area */
        pre {
            border-radius: 12px;
        }

        </style>
        """,
        unsafe_allow_html=True
    )
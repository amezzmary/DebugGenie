import streamlit as st
import base64
from pathlib import Path


def show_intro():

    video_path = Path(__file__).parent.parent / "Untitled design.mp4"

    with open(video_path, "rb") as video_file:
        video_bytes = video_file.read()

    video_base64 = base64.b64encode(video_bytes).decode()

    html = f"""
    <style>

    html, body, [data-testid="stAppViewContainer"] {{
        margin: 0;
        padding: 0;
        overflow: hidden;
        background:green;
    }}

    [data-testid="stHeader"] {{
        display: none;
    }}

    .video-container {{
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        background: black;
        z-index: 9999;
    }}

    .intro-video {{
        width: 100vw;
        height: 100vh;
        object-fit: cover;
        display: block;
    }}

    </style>

    <div class="video-container">
        <video
            class="intro-video"
            autoplay
            muted
            playsinline
            onended="goToHome()">

            <source src="data:video/mp4;base64,{video_base64}" type="video/mp4">

        </video>
    </div>

    <script>

    function goToHome() {{
        window.parent.location.href = "?page=home";
    }}

    </script>
    """

    st.components.v1.html(html, height=1000)
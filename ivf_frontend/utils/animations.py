import json
import requests
import streamlit as st

# -----------------------------------------------------------
# Utility functions for loading Lottie animations
# -----------------------------------------------------------

def load_lottie_file(filepath: str):
    """Load a local Lottie animation JSON file."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        st.error(f"Failed to load Lottie file: {e}")
        return None


def load_lottie_url(url: str):
    """Load Lottie animation from URL."""
    try:
        response = requests.get(url)
        if response.status_code != 200:
            st.error("Failed to fetch Lottie animation from URL.")
            return None
        return response.json()
    except Exception as e:
        st.error(f"Error loading Lottie URL: {e}")
        return None


# -----------------------------------------------------------
# Welcome Animation (Pink theme)
# -----------------------------------------------------------
def render_welcome_animation():
    st.markdown("""
    <style>
        @keyframes fadeInWelcome {
            from { opacity: 0; transform: translateY(20px); }
            to   { opacity: 1; transform: translateY(0); }
        }
        .welcome-box {
            animation: fadeInWelcome 1.1s ease-out;
            background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
            padding: 2rem;
            border-radius: var(--radius);
            text-align: center;
            color: white;
            box-shadow: 0 0 22px rgba(255, 120, 170, 0.45);
            margin-bottom: 1.5rem;
        }
        .welcome-box h2 {
            font-size: 1.9rem;
            margin-bottom: 0.6rem;
        }
        .welcome-box p {
            font-size: 1.05rem;
            opacity: 0.95;
        }
    </style>

    <div class="welcome-box">
        <h2>👶 Welcome to Your IVF Assistant</h2>
        <p>I’m here to help with compassionate, accurate IVF-related information.</p>
        <p><strong>You can ask about:</strong> treatments, procedures, medications, timelines, risks & more.</p>
    </div>
    """, unsafe_allow_html=True)


# -----------------------------------------------------------
# Typing Indicator Animation
# -----------------------------------------------------------
def render_typing_animation():
    st.markdown("""
    <style>
        @keyframes typingBlink {
            0%   { opacity: 0.3; }
            50%  { opacity: 1; }
            100% { opacity: 0.3; }
        }

        .typing-indicator {
            width: fit-content;
            padding: 0.8rem 1.1rem;
            margin: 0.5rem 0;
            border-radius: var(--radius);
            background: var(--primary-bg);
            border: 1px solid var(--border-color);
            box-shadow: 0 0 12px rgba(255, 150, 190, 0.35);
            display: flex;
            align-items: center;
        }

        .typing-dots span {
            height: 8px;
            width: 8px;
            margin-right: 4px;
            background: var(--accent-primary);
            border-radius: 50%;
            display: inline-block;
            animation: typingBlink 1.4s infinite;
        }

        .typing-dots span:nth-child(2) { animation-delay: 0.2s; }
        .typing-dots span:nth-child(3) { animation-delay: 0.4s; }
    </style>

    <div class="typing-indicator">
        <div class="typing-dots">
            <span></span><span></span><span></span>
        </div>
    </div>
    """, unsafe_allow_html=True)

"""
Session state management module
Streamlit 세션 상태를 초기화하고 관리합니다.
"""

import streamlit as st
import uuid


def initialize_session_state():
    """Session state를 초기화합니다."""
    if "thread_id" not in st.session_state:
        st.session_state.thread_id = str(uuid.uuid4())

    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "research_progress" not in st.session_state:
        st.session_state.research_progress = []

    if "current_stats" not in st.session_state:
        st.session_state.current_stats = {
            "queries": 0,
            "completed_searches": 0,
            "documents": 0,
            "reflections": 0,
        }

    # Initialize model and search configurations
    if "model_type" not in st.session_state:
        st.session_state.model_type = "vllm"

    if "search_type" not in st.session_state:
        st.session_state.search_type = "tavily"

    # Initialize API keys for user input
    if "user_gemini_api_key" not in st.session_state:
        st.session_state.user_gemini_api_key = ""

    if "user_tavily_api_key" not in st.session_state:
        st.session_state.user_tavily_api_key = ""

    if "user_google_api_key" not in st.session_state:
        st.session_state.user_google_api_key = ""

    # Track whether user settings have been applied
    if "settings_applied" not in st.session_state:
        st.session_state.settings_applied = False


def reset_research_progress():
    """리서치 진행 상황을 초기화합니다."""
    st.session_state.research_progress = []
    st.session_state.current_stats = {
        "queries": 0,
        "completed_searches": 0,
        "documents": 0,
        "reflections": 0,
    }


def clear_messages():
    """메시지 기록을 삭제합니다."""
    st.session_state.messages = []


def clear_session():
    """전체 세션을 초기화합니다."""
    st.session_state.clear()

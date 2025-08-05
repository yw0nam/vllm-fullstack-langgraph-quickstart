"""
Session state management module
Streamlit 세션 상태를 초기화하고 관리합니다.
"""

import os
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

    # Initialize user API keys only if they don't exist
    if "user_tavily_api_key" not in st.session_state:
        st.session_state.user_tavily_api_key = ""
    if "user_google_api_key" not in st.session_state:
        st.session_state.user_google_api_key = ""

    # Only set environment variables if they don't already exist or if user has provided values
    if st.session_state.user_tavily_api_key and not os.environ.get("TAVILY_API_KEY"):
        os.environ["TAVILY_API_KEY"] = st.session_state.user_tavily_api_key
    if st.session_state.user_google_api_key and not os.environ.get("GOOGLE_API_KEY"):
        os.environ["GOOGLE_API_KEY"] = st.session_state.user_google_api_key

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


def clear_session_with_api_keys():
    """전체 세션을 초기화하고 사용자 입력 API 키들을 삭제합니다."""
    import os
    from dotenv import load_dotenv
    
    # 현재 .env 파일의 원본 값들을 다시 로드
    load_dotenv(override=True)
    
    # .env 파일에 정의된 원본 키들을 저장
    original_tavily_key = os.getenv("TAVILY_API_KEY")
    original_google_key = os.getenv("GOOGLE_API_KEY")
    
    # 세션 상태 완전 초기화
    st.session_state.clear()
    
    # 환경변수를 .env 파일의 원본 값으로 복원
    if original_tavily_key:
        os.environ["TAVILY_API_KEY"] = original_tavily_key
    elif "TAVILY_API_KEY" in os.environ:
        del os.environ["TAVILY_API_KEY"]
        
    if original_google_key:
        os.environ["GOOGLE_API_KEY"] = original_google_key
    elif "GOOGLE_API_KEY" in os.environ:
        del os.environ["GOOGLE_API_KEY"]


def clear_session():
    """전체 세션을 초기화합니다."""
    st.session_state.clear()

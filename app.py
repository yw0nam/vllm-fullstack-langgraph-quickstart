"""
Modularized Streamlit App - Version 7

기존 streamlit_app_v6.py의 모든 기능을 유지하면서 코드를 모듈화했습니다.
- Config 관리 분리
- 세션 상태 관리 분리
- 사이드바 컴포넌트 분리
- 이벤트 스트림 처리 분리
- 응답 처리 분리
- 채팅 인터페이스 분리
"""

import streamlit as st
from agent import graph

# 모듈화된 컴포넌트들 import
from components.config import load_config, get_page_config
from components.session_state import initialize_session_state
from components.sidebar import SidebarManager
from components.chat_interface import ChatInterface
from components.logging_config import STREAMLIT_LOGGER


def main():
    """메인 애플리케이션 함수"""

    STREAMLIT_LOGGER.info("🚀 Starting Streamlit application...")

    # 설정 로드
    config = load_config()
    page_config = get_page_config()

    STREAMLIT_LOGGER.info("✅ Configuration loaded successfully")

    # Streamlit 페이지 설정
    st.set_page_config(**page_config)
    st.title("AI 리서치 에이전트 🔍")
    st.caption("Demonstrating the power of AI in real-time research!")

    # Session State 초기화
    initialize_session_state()
    STREAMLIT_LOGGER.info(
        f"📊 Session initialized - Thread ID: {st.session_state.thread_id}"
    )

    # 메인 컨테이너와 사이드바 구성
    col_main, col_sidebar = st.columns([2, 1])

    # 사이드바 설정
    with col_sidebar:
        sidebar_manager = SidebarManager(config)
        status_placeholder, stats_placeholder, progress_placeholder = (
            sidebar_manager.setup_sidebar()
        )

    # 메인 채팅 인터페이스
    with col_main:
        chat_interface = ChatInterface(graph, sidebar_manager)

        # 이전 대화 기록 표시
        chat_interface.render_chat_history()

        # 사용자 입력 처리
        chat_interface.handle_user_input()


if __name__ == "__main__":
    main()

"""
Chat interface module
메인 채팅 인터페이스와 메시지 처리를 관리합니다.
"""

import os
import streamlit as st
import traceback
from langchain_core.messages import HumanMessage
from .session_state import reset_research_progress
from .event_processor import EventStreamProcessor
from .response_processor import ResponseProcessor


def validate_configuration():
    """현재 모델 및 검색 설정이 유효한지 확인합니다."""
    errors = []

    # Model validation
    model_type = st.session_state.model_type
    if model_type == "vllm":
        if not os.getenv("MODEL_API_KEY") or not os.getenv("MODEL_API_URL"):
            errors.append(
                "vllm을 사용하려면 .env 파일에 MODEL_API_KEY와 MODEL_API_URL이 설정되어야 합니다."
            )
    elif model_type == "gemini":
        google_key = (
            os.getenv("GOOGLE_API_KEY") or st.session_state.user_google_api_key.strip()
        )
        if not google_key:
            errors.append("gemini를 사용하려면 Google API 키가 필요합니다.")

    # Search validation
    search_type = st.session_state.search_type
    if search_type == "tavily":
        tavily_key = (
            os.getenv("TAVILY_API_KEY") or st.session_state.user_tavily_api_key.strip()
        )
        if not tavily_key:
            errors.append("tavily 검색을 사용하려면 API 키가 필요합니다.")
    elif search_type == "google":
        google_key = (
            os.getenv("GOOGLE_API_KEY") or st.session_state.user_google_api_key.strip()
        )
        if not google_key:
            errors.append("google 검색을 사용하려면 Google API 키가 필요합니다.")

    return errors


class ChatInterface:
    """채팅 인터페이스 클래스"""

    def __init__(self, graph, sidebar_manager):
        self.graph = graph
        self.sidebar_manager = sidebar_manager
        self.event_processor = EventStreamProcessor(graph, sidebar_manager)
        self.response_processor = ResponseProcessor(graph, sidebar_manager)

    def render_chat_history(self):
        """이전 대화 기록을 화면에 표시합니다."""
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    def handle_user_input(self):
        """사용자 입력을 처리하고 AI 응답을 생성합니다."""
        if prompt := st.chat_input("어떤 주제에 대해 리서치해 드릴까요?"):
            # 설정 유효성 검사
            config_errors = validate_configuration()
            if config_errors:
                st.error("설정 오류가 발견되었습니다:")
                for error in config_errors:
                    st.error(f"• {error}")
                st.info("사이드바에서 설정을 확인하고 필요한 API 키를 입력해주세요.")
                return

            # 사용자 메시지를 기록하고 화면에 표시
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            # 진행 상황 초기화
            reset_research_progress()

            # 사이드바 초기 상태 업데이트
            self.sidebar_manager.initialize_sidebar_state()

            # 어시스턴트의 답변이 표시될 영역
            with st.chat_message("assistant"):
                self._process_ai_response(prompt)

    def _process_ai_response(self, prompt):
        """AI 응답을 처리합니다."""
        # 환경변수와 세션 상태에서 API 키를 가져옵니다
        google_api_key = (
            os.getenv("GOOGLE_API_KEY") or st.session_state.user_google_api_key.strip()
        )
        tavily_api_key = (
            os.getenv("TAVILY_API_KEY") or st.session_state.user_tavily_api_key.strip()
        )

        config = {
            "configurable": {
                "thread_id": st.session_state.thread_id,
                "search_type": st.session_state.search_type,
                "model_type": st.session_state.model_type,
                "google_api_key": google_api_key,
                "tavily_api_key": tavily_api_key,
            }
        }
        final_answer = ""

        try:
            # 이벤트 스트림 처리
            collected_data, stream_error = self.event_processor.process_stream(
                prompt, config
            )

            if stream_error:
                raise stream_error

            # 스트림 완료 후 최종 처리
            self.sidebar_manager.update_status("🔄 후처리 중", "결과 정리 중...")

            final_answer = collected_data.get("final_answer", "")

            # 최종 답변이 여전히 없으면 일반 invoke 시도
            if not final_answer:
                final_answer = self.response_processor.fallback_invoke(prompt, config)

            # <think> 태그 분리 및 결과 렌더링
            if final_answer:
                main_answer, reasoning_text = (
                    self.response_processor.separate_thinking_and_answer(final_answer)
                )

                # 최종 상태 업데이트
                self.sidebar_manager.update_status("✅ 완료", "리서치 완료!")

                # 결과 렌더링
                self.response_processor.render_final_result(
                    main_answer, reasoning_text, collected_data
                )
            else:
                st.markdown("### 📋 최종 리서치 결과")
                st.markdown("리서치를 완료했지만 답변을 생성하지 못했습니다.")

        except Exception as e:
            final_answer = self._handle_error_recovery(e, prompt, config)

        # 최종 답변을 세션 기록에 저장
        if final_answer:
            clean_answer = self.response_processor.clean_answer_for_session(
                final_answer
            )
            st.session_state.messages.append(
                {"role": "assistant", "content": clean_answer}
            )

    def _handle_error_recovery(self, error, prompt, config):
        """에러 발생 시 복구를 시도합니다."""
        self.sidebar_manager.update_status("❌ 오류 발생", f"에러: {str(error)}")
        st.error(f"❌ 치명적 에러가 발생했습니다: {str(error)}")
        st.error(f"상세 오류: {traceback.format_exc()}")

        # 에러 발생 시 일반 모드로 시도
        try:
            self.sidebar_manager.update_status(
                "🔄 복구 시도", "일반 모드로 재시도 중..."
            )

            result = self.graph.invoke(
                {"messages": [HumanMessage(content=prompt)]}, config
            )

            final_answer = ""
            if "messages" in result and result["messages"]:
                for msg in reversed(result["messages"]):
                    if (
                        hasattr(msg, "content")
                        and msg.content
                        and msg.content != prompt
                    ):
                        final_answer = msg.content
                        break

            # reasoning 분리
            main_answer, reasoning_text = (
                self.response_processor.separate_thinking_and_answer(final_answer)
            )

            self.sidebar_manager.update_status(
                "✅ 완료 (일반 모드)", "일반 모드로 완료"
            )

            # 최종 답변 먼저
            st.markdown("### 📋 최종 리서치 결과")
            st.markdown(main_answer or "답변을 생성하지 못했습니다.")

            # Reasoning 나중에 (참조 문서 전에)
            if reasoning_text:
                st.markdown("---")
                st.markdown("### 🧠 AI의 사고 과정")
                with st.expander("💭 Reasoning 과정 보기", expanded=False):
                    st.markdown(reasoning_text)

            return final_answer

        except Exception as e2:
            self.sidebar_manager.update_status(
                "❌ 심각한 오류", f"복구 불가능한 에러: {str(e2)}"
            )
            st.error(f"❌ 일반 모드에서도 에러 발생: {str(e2)}")
            st.error(f"상세 오류: {traceback.format_exc()}")

            final_answer = "죄송합니다. 요청을 처리하는 중 오류가 발생했습니다."
            st.markdown("### 📋 최종 리서치 결과")
            st.markdown(final_answer)

            return final_answer

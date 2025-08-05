"""
Response processing module
AI 응답 처리 및 스트리밍 관련 기능을 관리합니다.
"""

import re
import streamlit as st
import traceback
from langchain_core.messages import HumanMessage


class ResponseProcessor:
    """응답 처리 클래스"""

    def __init__(self, graph, sidebar_manager):
        self.graph = graph
        self.sidebar_manager = sidebar_manager

    def separate_thinking_and_answer(self, final_answer):
        """<think> 태그를 분리하여 reasoning과 main answer로 나눕니다."""
        reasoning_text = ""
        main_answer = final_answer

        if final_answer:
            # <think>...</think> 패턴 찾기
            think_pattern = r"<think>(.*?)</think>"
            think_matches = re.findall(think_pattern, final_answer, re.DOTALL)

            if think_matches:
                reasoning_text = "\n".join(think_matches)
                # <think> 태그 부분을 제거한 메인 답변
                main_answer = re.sub(
                    think_pattern, "", final_answer, flags=re.DOTALL
                ).strip()

        return main_answer, reasoning_text

    def render_final_result(self, main_answer, reasoning_text, collected_data):
        """최종 결과를 렌더링합니다."""
        # 최종 답변을 먼저 표시 (상단)
        st.markdown("### 📋 최종 리서치 결과")
        if main_answer:
            # 인용 링크를 실제 URL로 변환
            enhanced_answer = self._enhance_citations(main_answer, collected_data)
            st.markdown(enhanced_answer)
        else:
            st.markdown("리서치를 완료했지만 답변을 생성하지 못했습니다.")

        # Reasoning 부분을 메인 답변 다음에 표시
        if reasoning_text:
            st.markdown("---")
            st.markdown("### 🧠 AI의 사고 과정")
            with st.expander("💭 Reasoning 과정 보기", expanded=False):
                st.markdown(reasoning_text)

        # 모든 참조 문서 링크를 마지막에 표시
        if collected_data.get("sources_gathered"):
            st.markdown("---")
            st.markdown("### 📚 참조 문서")

            # 중복 제거된 소스 목록
            unique_sources = {}
            for source in collected_data["sources_gathered"]:
                url = source.get("value", "")
                if url and url not in unique_sources:
                    unique_sources[url] = source

            for i, (url, source) in enumerate(unique_sources.items(), 1):
                title = source.get("label", f"문서 {i}")
                st.markdown(f"{i}. [{title}]({url})")

    def _enhance_citations(self, text, collected_data):
        """텍스트의 인용 번호를 실제 URL 링크로 변환합니다."""
        if not collected_data.get("sources_gathered"):
            return text

        # short_url을 키로 하는 소스 매핑 생성
        source_mapping = {}
        for source in collected_data["sources_gathered"]:
            short_url = source.get("short_url", "")
            if short_url:
                source_mapping[short_url] = source

        # [label](short_url) 패턴 찾기
        import re

        citation_pattern = r"\[([^\]]+)\]\(([^)]+)\)"

        def replace_citation(match):
            label = match.group(1)
            short_url = match.group(2)

            # short_url로 실제 소스 찾기
            if short_url in source_mapping:
                source = source_mapping[short_url]
                url = source.get("url", source.get("value", ""))

                if url:
                    # 실제 URL로 링크 변환
                    return f"[[{label}]]({url})"

            # 매칭되는 소스가 없으면 원본 유지
            return match.group(0)

        # 모든 인용을 실제 링크로 변환
        enhanced_text = re.sub(citation_pattern, replace_citation, text)
        return enhanced_text

    def clean_answer_for_session(self, final_answer):
        """세션 저장용으로 <think> 태그를 제거한 깨끗한 답변을 반환합니다."""
        clean_answer = re.sub(
            r"<think>.*?</think>", "", final_answer, flags=re.DOTALL
        ).strip()
        return clean_answer or final_answer

    def fallback_invoke(self, prompt, config):
        """스트리밍 실패 시 일반 invoke를 시도합니다."""
        try:
            self.sidebar_manager.update_status(
                "🔄 후처리 중", "대체 방법으로 결과 가져오는 중..."
            )

            result = self.graph.invoke(
                {"messages": [HumanMessage(content=prompt)]}, config
            )

            if "messages" in result and result["messages"]:
                for msg in reversed(result["messages"]):
                    if (
                        hasattr(msg, "content")
                        and msg.content
                        and msg.content != prompt
                    ):
                        return msg.content
            return None
        except Exception as invoke_error:
            st.error(f"일반 invoke 중 오류: {str(invoke_error)}")
            return None

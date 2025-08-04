"""
Event stream processing module
LangGraph 이벤트 스트림을 처리하고 데이터를 수집합니다.
"""

import streamlit as st
import traceback
from langchain_core.messages import HumanMessage


class EventStreamProcessor:
    """이벤트 스트림 처리 클래스"""

    def __init__(self, graph, sidebar_manager):
        self.graph = graph
        self.sidebar_manager = sidebar_manager

    def process_stream(self, prompt, config):
        """이벤트 스트림을 처리하고 수집된 데이터를 반환합니다."""
        collected_data = {
            "queries": [],
            "research_results": [],
            "reflections": [],
            "final_answer": "",
            "sources_gathered": [],
            "total_documents": 0,
        }

        try:
            # 스트리밍 모드로 실행
            self.sidebar_manager.update_status(
                "🔄 LangGraph 실행 중", "이벤트 스트림 시작..."
            )

            events = self.graph.stream(
                {"messages": [HumanMessage(content=prompt)]},
                config,
                stream_mode="updates",
            )

            event_count = 0
            for event in events:
                try:
                    event_count += 1

                    # 이벤트가 비어있거나 None인 경우 건너뛰기
                    if not event:
                        continue

                    # 디버그 정보 표시
                    with st.expander(f"🔍 이벤트 #{event_count}", expanded=False):
                        st.write(f"키: {list(event.keys()) if event else 'None'}")
                        st.json(event)

                    # 각 노드별 업데이트 처리
                    for node_name, node_data in event.items():
                        self._process_node_event(node_name, node_data, collected_data)

                except Exception as event_error:
                    st.warning(
                        f"⚠️ 이벤트 #{event_count} 처리 중 오류: {str(event_error)}"
                    )
                    st.error(f"상세 오류: {traceback.format_exc()}")
                    continue

            return collected_data, None

        except Exception as e:
            return collected_data, e

    def _process_node_event(self, node_name, node_data, collected_data):
        """개별 노드 이벤트를 처리합니다."""
        try:
            # node_data가 비어있거나 None인 경우 건너뛰기
            if not node_data:
                return

            # 현재 진행 상황 업데이트
            current_status = f"🔄 {node_name} 실행 중"

            if node_name == "generate_query":
                self._process_generate_query(node_data, collected_data, current_status)

            elif node_name == "web_research":
                self._process_web_research(node_data, collected_data, current_status)

            elif node_name == "reflection":
                self._process_reflection(node_data, collected_data, current_status)

            elif node_name == "finalize_answer":
                self._process_finalize_answer(node_data, collected_data, current_status)

        except Exception as node_error:
            st.warning(f"⚠️ 노드 '{node_name}' 처리 중 오류: {str(node_error)}")
            st.error(f"상세 오류: {traceback.format_exc()}")

    def _process_generate_query(self, node_data, collected_data, current_status):
        """generate_query 노드 이벤트를 처리합니다."""
        self.sidebar_manager.update_status(current_status, "검색어 생성 중...")

        if "query_list" in node_data and node_data["query_list"]:
            collected_data["queries"] = node_data["query_list"]
            st.session_state.current_stats["queries"] = len(collected_data["queries"])

            # 진행 상황에 추가
            progress_item = {
                "type": "generate_query",
                "content": f"✅ {len(collected_data['queries'])}개의 검색어를 생성했습니다!",
                "details": collected_data["queries"],
            }
            st.session_state.research_progress.append(progress_item)

            # 사이드바 업데이트
            self.sidebar_manager.update_stats()
            self.sidebar_manager.update_progress()

    def _process_web_research(self, node_data, collected_data, current_status):
        """web_research 노드 이벤트를 처리합니다."""
        self.sidebar_manager.update_status(current_status, "웹 리서치 실행 중...")

        # v6과 동일한 키 구조 사용
        if (
            "search_query" in node_data
            and "web_research_result" in node_data
        ):
            query = (
                node_data["search_query"][0]
                if node_data.get("search_query")
                else "Unknown"
            )
            result = (
                node_data["web_research_result"][0]
                if node_data.get("web_research_result")
                else ""
            )

            # sources_gathered 정보 수집
            sources = node_data.get("sources_gathered", [])
            if sources:
                collected_data["sources_gathered"].extend(sources)
                
                # 중복 URL 제거하여 정확한 문서 수 계산
                unique_urls = set()
                for source in collected_data["sources_gathered"]:
                    url = source.get("url", source.get("value", ""))
                    if url:
                        unique_urls.add(url)
                
                collected_data["total_documents"] = len(unique_urls)

            # 리서치 결과 추가
            research_result = {
                "query": query,
                "result": result,
                "sources": sources,
            }
            collected_data["research_results"].append(research_result)

            # 세션 상태 업데이트
            st.session_state.current_stats["completed_searches"] = len(
                collected_data["research_results"]
            )
            st.session_state.current_stats["documents"] = len(
                collected_data["sources_gathered"]
            )

            # 진행 상황에 추가
            doc_count = len(sources) if sources else 0
            progress_item = {
                "type": "web_research",
                "content": f"🔍 '{query}' 검색 완료 ({doc_count}개 문서 참조)",
                "query": query,
                "result": result,
                "sources": sources,
            }
            st.session_state.research_progress.append(progress_item)

            # 사이드바 업데이트
            self.sidebar_manager.update_status(
                current_status, f"'{query}' 검색 완료 ({len(sources)}개 문서)"
            )
            self.sidebar_manager.update_stats()
            self.sidebar_manager.update_progress()

    def _process_reflection(self, node_data, collected_data, current_status):
        """reflection 노드 이벤트를 처리합니다."""
        self.sidebar_manager.update_status(current_status, "성찰 중...")

        if "reflection_result" in node_data and node_data["reflection_result"]:
            reflection_result = node_data["reflection_result"]
            collected_data["reflections"].append(reflection_result)

            # 성찰 결과 분석
            knowledge_gap = reflection_result.get("knowledge_gap", "알 수 없음")
            is_sufficient = reflection_result.get("is_sufficient", False)

            # 통계 업데이트
            st.session_state.current_stats["reflections"] = len(
                collected_data["reflections"]
            )

            # 진행 상황에 추가
            if is_sufficient:
                content = "✅ 충분한 정보를 수집했습니다!"
                step = "충분한 정보 수집 완료"
            else:
                content = f"🤔 추가 정보 필요: {knowledge_gap}"
                step = f"추가 정보 필요: {knowledge_gap[:50]}..."

            progress_item = {
                "type": "reflection",
                "content": content,
                "knowledge_gap": knowledge_gap,
                "is_sufficient": is_sufficient,
            }
            st.session_state.research_progress.append(progress_item)

            # 사이드바 업데이트
            self.sidebar_manager.update_status(current_status, step)
            self.sidebar_manager.update_stats()
            self.sidebar_manager.update_progress()

    def _process_finalize_answer(self, node_data, collected_data, current_status):
        """finalize_answer 노드 이벤트를 처리합니다."""
        self.sidebar_manager.update_status(current_status, "최종 보고서 작성 중...")

        if "messages" in node_data and node_data["messages"]:
            final_answer = node_data["messages"][-1].content
            collected_data["final_answer"] = final_answer

            # 사이드바 업데이트
            self.sidebar_manager.update_status("✅ 완료", "최종 보고서 작성 완료!")

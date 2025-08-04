"""
Sidebar components module
사이드바의 진행 상황 표시 및 컨트롤을 관리합니다.
"""

import streamlit as st
import os


class SidebarManager:
    """사이드바 관리 클래스"""

    def __init__(self, config):
        self.config = config
        self.status_placeholder = None
        self.stats_placeholder = None
        self.progress_placeholder = None

    def setup_sidebar(self):
        """사이드바를 설정하고 플레이스홀더를 생성합니다."""
        st.markdown("## ⚙️ 설정")

        # Model Type Selection
        self._render_model_selection()

        st.markdown("---")

        # Search Type Selection
        self._render_search_selection()

        st.markdown("---")

        st.markdown("## 📊 리서치 진행 상황")

        # 실시간 업데이트를 위한 플레이스홀더들
        self.status_placeholder = st.empty()
        self.stats_placeholder = st.empty()
        self.progress_placeholder = st.empty()

        st.markdown("---")

        # 컨트롤
        self._render_controls()

        st.markdown("---")

        # 디버그 정보
        self._render_debug_info()

        # 환경 설정
        self._render_env_info()

        # 사용법 안내
        self._render_usage_guide()

        return (
            self.status_placeholder,
            self.stats_placeholder,
            self.progress_placeholder,
        )

    def _render_model_selection(self):
        """모델 타입 선택을 렌더링합니다."""
        st.markdown("### 🤖 모델 선택")

        model_type = st.selectbox(
            "Model Type",
            ["vllm", "gemini"],
            index=0 if st.session_state.model_type == "vllm" else 1,
            key="model_selectbox",
            help="사용할 언어 모델을 선택하세요",
        )

        # Update session state
        st.session_state.model_type = model_type

        # Show API key input for gemini
        if model_type == "gemini":
            gemini_api_key = st.text_input(
                "google API Key",
                value=st.session_state.user_gemini_api_key,
                type="password",
                key="gemini_key_input",
                help="gemini 모델 사용을 위한 google API 키를 입력하세요",
                placeholder="google API 키를 입력하세요...",
            )
            st.session_state.user_gemini_api_key = gemini_api_key

            if not gemini_api_key:
                st.warning("⚠️ gemini 사용을 위해서는 google API 키가 필요합니다.")
            elif gemini_api_key and gemini_api_key != self.config.get("google_api_key"):
                st.info(
                    "💡 API 키를 입력했습니다. '✅ 설정 적용' 버튼을 눌러 적용하세요."
                )
        else:
            # Show vllm status
            vllm_configured = self.config.get("api_key") and self.config.get(
                "api_base_url"
            )
            if vllm_configured:
                st.success("✅ vllm 설정이 완료되었습니다.")
            else:
                st.error("❌ vllm 설정이 완료되지 않았습니다. .env 파일을 확인하세요.")

    def _render_search_selection(self):
        """검색 타입 선택을 렌더링합니다."""
        st.markdown("### 🔍 검색 엔진 선택")

        search_type = st.selectbox(
            "Search Type",
            ["tavily", "google"],
            index=0 if st.session_state.search_type == "tavily" else 1,
            key="search_selectbox",
            help="사용할 검색 엔진을 선택하세요",
        )

        # Update session state
        st.session_state.search_type = search_type

        if search_type == "tavily":
            # Check if tavily API key is configured in .env
            env_tavily_key = self.config.get("tavily_api_key")
            if env_tavily_key:
                st.success("✅ tavily API 키가 환경변수에서 로드되었습니다.")
            else:
                # Show input for tavily API key
                tavily_api_key = st.text_input(
                    "tavily API Key",
                    value=st.session_state.user_tavily_api_key,
                    type="password",
                    key="tavily_key_input",
                    help="tavily 검색을 위한 API 키를 입력하세요",
                    placeholder="tavily API 키를 입력하세요...",
                )
                st.session_state.user_tavily_api_key = tavily_api_key

                if not tavily_api_key:
                    st.warning("⚠️ tavily 검색을 위해서는 API 키가 필요합니다.")
                elif tavily_api_key != self.config.get("tavily_api_key"):
                    st.info(
                        "💡 API 키를 입력했습니다. '✅ 설정 적용' 버튼을 눌러 적용하세요."
                    )

        elif search_type == "google":
            # google Search always uses gemini's google Search grounding feature
            # This requires a google API key regardless of the selected model
            env_google_key = self.config.get("google_api_key")

            if env_google_key:
                st.success("✅ google API 설정이 환경변수에서 로드되었습니다.")
            else:
                # Show input for google API configuration
                google_api_key = st.text_input(
                    "google API Key",
                    value=st.session_state.user_google_api_key,
                    type="password",
                    key="google_key_input",
                    help="google Search grounding을 위한 google API 키를 입력하세요",
                    placeholder="google API 키를 입력하세요...",
                )
                st.session_state.user_google_api_key = google_api_key

                if not google_api_key:
                    st.warning("⚠️ google 검색을 위해서는 google API 키가 필요합니다.")
                elif google_api_key != self.config.get("google_api_key"):
                    st.info(
                        "💡 API 키를 입력했습니다. '✅ 설정 적용' 버튼을 눌러 적용하세요."
                    )

        # Show configuration validation
        self._show_configuration_validation()

    def _render_controls(self):
        """컨트롤 버튼들을 렌더링합니다."""
        st.markdown("## 🛠️ 컨트롤")

        # Apply Settings button with dynamic styling
        has_pending = self._has_pending_settings()
        button_text = "✅ 설정 적용" + (" 🔔" if has_pending else "")
        button_help = "입력한 API 키를 현재 세션에 적용합니다" + (
            " (적용 대기 중인 설정 있음)" if has_pending else ""
        )

        if st.button(button_text, help=button_help):
            self._apply_user_settings()

        st.markdown("---")

        if st.button("🗑️ 대화 기록 삭제"):
            st.session_state.messages = []
            st.rerun()

        if st.button("🔄 세션 초기화"):
            st.session_state.clear()
            st.rerun()

    def _apply_user_settings(self):
        """사용자가 입력한 API 키들을 현재 설정에 적용합니다."""
        import os

        applied_settings = []

        # Apply google API key (for both gemini model and google Search)
        # Priority: use the key from the currently selected model/search combination
        google_api_key_to_apply = None

        if (
            st.session_state.model_type == "gemini"
            and st.session_state.user_gemini_api_key.strip()
        ):
            google_api_key_to_apply = st.session_state.user_gemini_api_key.strip()
            applied_settings.append("gemini API Key")
        elif (
            st.session_state.search_type == "google"
            and st.session_state.user_google_api_key.strip()
        ):
            google_api_key_to_apply = st.session_state.user_google_api_key.strip()
            applied_settings.append("google API Key")

        # Apply the google API key if we have one
        if google_api_key_to_apply:
            os.environ["GOOGLE_API_KEY"] = google_api_key_to_apply
            self.config["google_api_key"] = google_api_key_to_apply

        # Apply tavily API key if provided
        if st.session_state.user_tavily_api_key.strip():
            os.environ["TAVILY_API_KEY"] = st.session_state.user_tavily_api_key.strip()
            self.config["tavily_api_key"] = st.session_state.user_tavily_api_key.strip()
            applied_settings.append("tavily API Key")

        # Show success message
        if applied_settings:
            st.session_state.settings_applied = True
            st.success(f"✅ 다음 설정이 적용되었습니다: {', '.join(applied_settings)}")
            st.info(
                "💡 변경사항이 현재 세션에 적용되었습니다. 새로운 대화에서 사용됩니다."
            )
            # Force a rerun to update the UI
            st.rerun()
        else:
            st.warning("⚠️ 적용할 API 키가 없습니다. 먼저 API 키를 입력해주세요.")

    def _has_pending_settings(self):
        """적용되지 않은 사용자 설정이 있는지 확인합니다."""
        # Check for pending tavily API key
        tavily_pending = (
            st.session_state.user_tavily_api_key.strip()
            and st.session_state.user_tavily_api_key.strip()
            != self.config.get("tavily_api_key", "")
        )

        # Check for pending google API key (from either gemini model or google Search)
        google_pending = False
        if st.session_state.model_type == "gemini":
            google_pending = (
                st.session_state.user_gemini_api_key.strip()
                and st.session_state.user_gemini_api_key.strip()
                != self.config.get("google_api_key", "")
            )
        elif st.session_state.search_type == "google":
            google_pending = (
                st.session_state.user_google_api_key.strip()
                and st.session_state.user_google_api_key.strip()
                != self.config.get("google_api_key", "")
            )

        return tavily_pending or google_pending

    def _show_configuration_validation(self):
        """현재 모델과 검색 엔진 조합의 유효성을 검사하고 표시합니다."""
        model_type = st.session_state.model_type
        search_type = st.session_state.search_type

        # Check if we have the required API keys
        has_vllm_config = self.config.get("api_key") and self.config.get("api_base_url")
        has_google_api_key = (
            self.config.get("google_api_key")
            or st.session_state.user_gemini_api_key
            or st.session_state.user_google_api_key
        )
        has_tavily_api_key = (
            self.config.get("tavily_api_key") or st.session_state.user_tavily_api_key
        )

        # Validate combinations and show appropriate messages
        if model_type == "vllm" and search_type == "google":
            if has_vllm_config and has_google_api_key:
                st.success("✅ vllm + google Search 조합이 올바르게 설정되었습니다.")
            elif not has_vllm_config:
                st.error("❌ vllm 설정이 필요합니다. .env 파일을 확인하세요.")

        elif model_type == "vllm" and search_type == "tavily":
            if has_vllm_config and has_tavily_api_key:
                st.success("✅ vllm + tavily 조합이 올바르게 설정되었습니다.")
            elif not has_vllm_config:
                st.error("❌ vllm 설정이 필요합니다. .env 파일을 확인하세요.")

        elif model_type == "gemini" and search_type == "google":
            if has_google_api_key:
                st.success("✅ gemini + google Search 조합이 올바르게 설정되었습니다.")
                st.info("💡 gemini API 키가 모델과 검색에 공통으로 사용됩니다.")
            else:
                st.warning("⚠️ gemini 모델과 google Search를 위한 API 키가 필요합니다.")

        elif model_type == "gemini" and search_type == "tavily":
            missing_keys = []
            if not has_google_api_key:
                missing_keys.append("google API Key (gemini 모델용)")
            if not has_tavily_api_key:
                missing_keys.append("tavily API Key (검색용)")

            if not missing_keys:
                st.success("✅ gemini + tavily 조합이 올바르게 설정되었습니다.")
            else:
                st.warning(f"⚠️ 다음 API 키가 필요합니다: {', '.join(missing_keys)}")

    def _render_debug_info(self):
        """디버그 정보를 렌더링합니다."""
        st.markdown("## 📊 디버그 정보")
        st.write(f"**Thread ID:** `{st.session_state.thread_id}`")
        st.write(f"**메시지 수:** {len(st.session_state.messages)}")

    def _render_env_info(self):
        """환경 설정 정보를 렌더링합니다."""
        st.markdown("## 🔧 현재 설정")

        # Model Configuration
        st.write(f"**선택된 모델:** {st.session_state.model_type}")
        if st.session_state.model_type == "vllm":
            st.write(f"**vllm API URL:** `{self.config.get('api_base_url', 'N/A')}`")
            st.write(
                f"**vllm API Key:** {'✅ 설정됨' if self.config.get('api_key') else '❌ 설정되지 않음'}"
            )
        elif st.session_state.model_type == "gemini":
            # Check both config and user input for gemini
            effective_gemini_key = (
                self.config.get("google_api_key")
                or st.session_state.user_gemini_api_key
            )
            gemini_key_status = (
                "✅ 설정됨" if effective_gemini_key else "❌ 설정되지 않음"
            )

            # Show source of the key
            if (
                self.config.get("google_api_key")
                and st.session_state.user_gemini_api_key
            ):
                key_source = "(환경변수 + 사용자입력 병합됨)"
            elif self.config.get("google_api_key"):
                key_source = "(환경변수에서)"
            elif st.session_state.user_gemini_api_key:
                key_source = "(사용자입력 - 적용 필요)"
            else:
                key_source = ""

            st.write(f"**gemini API Key:** {gemini_key_status} {key_source}")

        # Search Configuration
        st.write(f"**선택된 검색:** {st.session_state.search_type}")
        if st.session_state.search_type == "tavily":
            effective_tavily_key = (
                self.config.get("tavily_api_key")
                or st.session_state.user_tavily_api_key
            )
            tavily_status = "✅ 설정됨" if effective_tavily_key else "❌ 설정되지 않음"

            # Show source of the key
            if (
                self.config.get("tavily_api_key")
                and st.session_state.user_tavily_api_key
            ):
                key_source = "(환경변수 + 사용자입력 병합됨)"
            elif self.config.get("tavily_api_key"):
                key_source = "(환경변수에서)"
            elif st.session_state.user_tavily_api_key:
                key_source = "(사용자입력 - 적용 필요)"
            else:
                key_source = ""

            st.write(f"**tavily API Key:** {tavily_status} {key_source}")

        elif st.session_state.search_type == "google":
            # For google Search, check the appropriate key based on model selection
            if st.session_state.model_type == "gemini":
                # If using gemini model, use the gemini API key for search too
                effective_google_key = (
                    self.config.get("google_api_key")
                    or st.session_state.user_gemini_api_key
                )
                key_source_info = "gemini API 키 사용"
            else:
                # If using other model (e.g., vllm), need separate google API key for search
                effective_google_key = (
                    self.config.get("google_api_key")
                    or st.session_state.user_google_api_key
                )
                key_source_info = "google Search 전용"

            google_key_status = (
                "✅ 설정됨" if effective_google_key else "❌ 설정되지 않음"
            )

            # Show source of the key
            if self.config.get("google_api_key"):
                if (
                    st.session_state.model_type == "gemini"
                    and st.session_state.user_gemini_api_key
                ):
                    key_source = f"(환경변수 + 사용자입력 병합됨, {key_source_info})"
                elif (
                    st.session_state.model_type != "gemini"
                    and st.session_state.user_google_api_key
                ):
                    key_source = f"(환경변수 + 사용자입력 병합됨, {key_source_info})"
                else:
                    key_source = f"(환경변수에서, {key_source_info})"
            else:
                if (
                    st.session_state.model_type == "gemini"
                    and st.session_state.user_gemini_api_key
                ):
                    key_source = f"(사용자입력 - 적용 필요, {key_source_info})"
                elif (
                    st.session_state.model_type != "gemini"
                    and st.session_state.user_google_api_key
                ):
                    key_source = f"(사용자입력 - 적용 필요, {key_source_info})"
                else:
                    key_source = f"({key_source_info})"

            st.write(f"**google API Key:** {google_key_status} {key_source}")
            st.caption("🔍 google Search grounding 사용")

    def _render_usage_guide(self):
        """사용법 안내를 렌더링합니다."""
        st.markdown("## 📖 사용법")
        st.markdown(
            """
        1. 좌측 입력창에 리서치하고 싶은 주제를 입력하세요
        2. AI가 자동으로 검색어를 생성하고 웹 리서치를 수행합니다
        3. 진행 상황은 우측 패널에서 실시간으로 확인할 수 있습니다
        4. 최종 답변이 먼저 표시되고, AI의 사고 과정은 접어서 확인할 수 있습니다
        """
        )

    def update_status(self, status, step):
        """사이드바 상태 업데이트 함수"""
        try:
            with self.status_placeholder.container():
                st.markdown("### 🔄 현재 상태")
                st.info(f"**상태**: {status}")
                st.info(f"**단계**: {step}")
        except Exception as e:
            st.error(f"상태 업데이트 오류: {e}")

    def update_stats(self):
        """사이드바 통계 업데이트 함수"""
        try:
            with self.stats_placeholder.container():
                st.markdown("### 📈 통계")
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("검색어", st.session_state.current_stats["queries"])
                    st.metric(
                        "완료된 검색",
                        st.session_state.current_stats["completed_searches"],
                    )
                with col2:
                    st.metric("참조 문서", st.session_state.current_stats["documents"])
                    st.metric(
                        "성찰 횟수", st.session_state.current_stats["reflections"]
                    )
        except Exception as e:
            st.error(f"통계 업데이트 오류: {e}")

    def update_progress(self):
        """사이드바 진행 과정 업데이트 함수"""
        try:
            with self.progress_placeholder.container():
                if st.session_state.research_progress:
                    st.markdown("### 🔄 상세 진행 과정")

                    for i, item in enumerate(st.session_state.research_progress):
                        if item["type"] == "generate_query":
                            st.success(item["content"])
                            with st.expander("🔍 생성된 검색어", expanded=False):
                                for j, query in enumerate(item["details"], 1):
                                    st.write(f"{j}. {query}")

                        elif item["type"] == "web_research":
                            st.info(item["content"])
                            with st.expander(
                                f"'{item['query']}' 검색 결과", expanded=False
                            ):
                                st.markdown(item["result"])

                                # 참조된 소스 표시
                                if item.get("sources"):
                                    st.markdown("**참조 문서:**")
                                    for j, source in enumerate(item["sources"], 1):
                                        source_url = source.get(
                                            "url", source.get("value", "Unknown")
                                        )
                                        source_title = source.get("title", f"문서 {j}")
                                        st.markdown(
                                            f"{j}. [{source_title}]({source_url})"
                                        )

                        elif item["type"] == "reflection":
                            if item.get("is_sufficient"):
                                st.success(item["content"])
                            else:
                                st.warning(item["content"])
        except Exception as e:
            st.error(f"진행 과정 업데이트 오류: {e}")

    def initialize_sidebar_state(self):
        """사이드바 초기 상태를 설정합니다."""
        self.update_status("🚀 리서치 시작", "초기화 중...")

        with self.stats_placeholder.container():
            st.markdown("### 📈 통계")
            col1, col2 = st.columns(2)
            with col1:
                st.metric("검색어", 0)
                st.metric("완료된 검색", 0)
            with col2:
                st.metric("참조 문서", 0)
                st.metric("성찰 횟수", 0)

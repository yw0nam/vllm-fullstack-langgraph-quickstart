"""
Centralized logging configuration for the AI Research Agent
모든 모듈에서 사용할 중앙집중식 로깅 시스템
"""

import logging
import sys
from datetime import datetime
from pathlib import Path

# 로그 디렉토리 생성
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)


def setup_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """
    로거를 설정하고 반환합니다.

    Args:
        name: 로거 이름 (보통 모듈명)
        level: 로그 레벨

    Returns:
        설정된 로거
    """
    logger = logging.getLogger(name)

    # 이미 핸들러가 있으면 중복 추가 방지
    if logger.handlers:
        return logger

    logger.setLevel(level)

    # 포맷터 설정
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # 콘솔 핸들러
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # 파일 핸들러 (일별 로그 파일)
    today = datetime.now().strftime("%Y-%m-%d")
    file_handler = logging.FileHandler(LOG_DIR / f"agent_{today}.log", encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)  # 파일에는 모든 레벨 기록
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger


def log_api_call(
    logger: logging.Logger,
    endpoint: str,
    method: str = "POST",
    data: str = None,
    response_status: str = None,
):
    """API 호출을 로깅합니다."""
    log_msg = f"API Call - {method} {endpoint}"
    if response_status:
        log_msg += f" | Status: {response_status}"
    if data:
        # 데이터가 너무 길면 자름
        data_preview = data[:200] + "..." if len(data) > 200 else data
        log_msg += f" | Data: {data_preview}"
    logger.info(log_msg)


def log_graph_transition(
    logger: logging.Logger, from_node: str, to_node: str, state_data: dict = None
):
    """그래프 노드 전환을 로깅합니다."""
    log_msg = f"Graph Transition: {from_node} -> {to_node}"
    if state_data:
        # 중요한 상태 정보만 로깅
        important_keys = ["search_query", "research_loop_count", "is_sufficient"]
        filtered_state = {k: v for k, v in state_data.items() if k in important_keys}
        if filtered_state:
            log_msg += f" | State: {filtered_state}"
    logger.info(log_msg)


def log_tool_usage(
    logger: logging.Logger,
    tool_name: str,
    input_data: str = None,
    output_data: str = None,
    success: bool = True,
):
    """도구 사용을 로깅합니다."""
    status = "SUCCESS" if success else "FAILED"
    log_msg = f"Tool Usage - {tool_name} | Status: {status}"

    if input_data:
        input_preview = (
            input_data[:100] + "..." if len(input_data) > 100 else input_data
        )
        log_msg += f" | Input: {input_preview}"

    if output_data:
        output_preview = (
            output_data[:100] + "..." if len(output_data) > 100 else output_data
        )
        log_msg += f" | Output: {output_preview}"

    logger.info(log_msg)


def log_error_with_context(
    logger: logging.Logger, error: Exception, context: str, additional_data: dict = None
):
    """에러를 컨텍스트와 함께 로깅합니다."""
    log_msg = f"ERROR in {context} | {type(error).__name__}: {str(error)}"
    if additional_data:
        log_msg += f" | Context: {additional_data}"
    logger.error(log_msg, exc_info=True)


# 각 모듈별 로거 미리 설정
GRAPH_LOGGER = setup_logger("agent.graph")
UTILS_LOGGER = setup_logger("agent.utils")
TOOLS_LOGGER = setup_logger("agent.tools")
STREAMLIT_LOGGER = setup_logger("streamlit.app")
API_LOGGER = setup_logger("api.client")

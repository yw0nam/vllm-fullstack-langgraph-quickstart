"""
Configuration module for the Streamlit app
환경 변수 및 기본 설정을 관리합니다.
"""

import os
from dotenv import load_dotenv


def load_config():
    """환경 변수를 로드하고 설정을 반환합니다."""
    load_dotenv()

    # Default vLLM configuration from environment
    api_key = os.getenv("MODEL_API_KEY")
    api_base_url = os.getenv("MODEL_API_URL")

    # Search API keys from environment
    tavily_api_key = os.getenv("TAVILY_API_KEY")
    google_api_key = os.getenv("GOOGLE_API_KEY")

    # Check if at least vLLM config is available as fallback
    if not api_key:
        print("⚠️ 경고: .env 파일에서 vLLM api_key 찾을 수 없습니다!")
        print("Gemini API를 사용하시거나 .env 파일을 확인해주세요.")

    print(f"✅ 환경 변수를 읽었습니다.")
    print(f"   - vLLM API Base URL: {api_base_url}")
    print(f"   - vLLM API Key: {'설정됨' if api_key else '설정되지 않음'}")
    print(f"   - Tavily API Key: {'설정됨' if tavily_api_key else '설정되지 않음'}")
    print(f"   - Google API Key: {'설정됨' if google_api_key else '설정되지 않음'}")
    print("-" * 30)

    return {
        "api_key": api_key,
        "api_base_url": api_base_url,
        "tavily_api_key": tavily_api_key,
        "google_api_key": google_api_key,
    }


def get_page_config():
    """Streamlit 페이지 설정을 반환합니다."""
    return {
        "page_title": "AI 리서치 에이전트",
        "page_icon": "🔍",
        "layout": "wide",
    }

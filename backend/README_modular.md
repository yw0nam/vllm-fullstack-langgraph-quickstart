# 나츠메의 AI 리서치 에이전트 - 모듈화 버전

## 📁 프로젝트 구조

### 버전별 파일
- `streamlit_app_v6.py` - 이전 단일 파일 버전 (작동 확인됨)
- `streamlit_app_v7.py` - **새로운 모듈화 버전** (권장)

### 모듈 구조
```
components/
├── __init__.py
├── config.py              # 환경 설정 관리
├── session_state.py       # Streamlit 세션 상태 관리
├── sidebar.py             # 사이드바 컴포넌트 (진행 상황, 통계, 컨트롤)
├── event_processor.py     # LangGraph 이벤트 스트림 처리
├── response_processor.py  # AI 응답 처리 (<think> 태그 분리 등)
└── chat_interface.py      # 메인 채팅 인터페이스
```

## 🚀 실행 방법

### 기본 실행
```bash
uv run streamlit run streamlit_app_v7.py
```

## 📋 주요 기능

### 1. 실시간 리서치 진행 상황 표시
- 우측 사이드바에서 실시간 상태 확인
- 검색어 생성, 웹 리서치, 성찰 과정을 단계별 표시
- 통계 정보 (검색어 수, 완료된 검색, 참조 문서 수, 성찰 횟수)

### 2. 구조화된 답변 표시
- **최종 답변** 먼저 표시
- **AI 사고 과정** (`<think>` 태그 내용) 접을 수 있는 형태로 표시
- **참조 문서** 링크 목록을 마지막에 표시

### 3. 에러 처리 및 복구
- 스트리밍 실패 시 자동으로 일반 모드로 전환
- 상세한 에러 로그 및 디버그 정보 제공
- 다중 레벨 예외 처리

### 4. 세션 관리
- 대화 기록 유지
- 세션 초기화 및 대화 기록 삭제 기능
- 고유 Thread ID를 통한 세션 관리

## 🔧 모듈별 설명

### `config.py`
- 환경 변수 로드 (.env 파일)
- Streamlit 페이지 설정 관리
- API 키 및 URL 검증

### `session_state.py`
- Streamlit 세션 상태 초기화
- 리서치 진행 상황 초기화
- 메시지 및 세션 클리어 기능

### `sidebar.py`
- 진행 상황 실시간 업데이트
- 통계 표시 (검색어, 문서, 성찰 등)
- 컨트롤 버튼 (초기화, 삭제)
- 디버그 정보 및 사용법 안내

### `event_processor.py`
- LangGraph 이벤트 스트림 처리
- 노드별 이벤트 분석 (generate_query, web_research, reflection, finalize_answer)
- 데이터 수집 및 통계 업데이트

### `response_processor.py`
- `<think>` 태그 분리 및 처리
- 최종 결과 렌더링 (답변 → 사고과정 → 참조문서 순서)
- 세션 저장용 답변 정리
- 스트리밍 실패 시 fallback 처리

### `chat_interface.py`
- 메인 채팅 인터페이스 관리
- 사용자 입력 처리
- AI 응답 생성 및 에러 복구
- 대화 기록 표시

## 🎯 개선 사항

### v6 → v7 변경점
1. **모듈화**: 600+ 줄의 단일 파일을 7개 모듈로 분리
2. **유지보수성**: 각 기능별로 클래스화하여 코드 관리 용이
3. **재사용성**: 컴포넌트 단위로 분리하여 다른 프로젝트에서 재사용 가능
4. **가독성**: 각 모듈의 역할이 명확하여 코드 이해도 향상
5. **확장성**: 새로운 기능 추가 시 해당 모듈만 수정하면 됨

### 기존 기능 유지
- ✅ 실시간 스트리밍 처리
- ✅ `<think>` 태그 분리 및 순서 (답변 → 사고과정 → 참조문서)
- ✅ 사이드바 실시간 업데이트
- ✅ 에러 처리 및 복구
- ✅ 세션 관리
- ✅ 디버그 정보 표시

## 🐛 트러블슈팅

### 모듈 import 에러
```bash
# 현재 디렉토리에서 실행해야 함
cd /path/to/backend
streamlit run streamlit_app_v7.py
```

### 환경 변수 에러
```bash
# .env 파일 확인
cat .env
# MODEL_API_URL과 MODEL_API_KEY가 설정되어 있는지 확인
```

## 📝 개발 히스토리

- **v1-v5**: 초기 개발 및 스트리밍 문제 해결
- **v6**: 완전한 기능 구현 (단일 파일)
- **v7**: 모듈화 완료 ✨

## 🤝 기여 방법

새로운 기능을 추가하거나 버그를 수정할 때:

1. 해당 기능과 관련된 모듈을 찾기
2. 모듈 내의 적절한 클래스/메서드 수정
3. 필요시 새로운 모듈 생성
4. `streamlit_app_v7.py`에서 새 모듈 import 및 사용

예시:
```python
# 새로운 기능을 위한 모듈
from components.new_feature import NewFeatureManager

# main() 함수에서 사용
new_feature = NewFeatureManager()
new_feature.do_something()
```

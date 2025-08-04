# AI 리서치 에이전트 - 모델 및 검색 선택 기능

이제 AI 리서치 에이전트에서 사용할 모델과 검색 엔진을 선택할 수 있습니다!

## 새로운 기능

### 🤖 모델 선택
사이드바에서 사용할 언어 모델을 선택할 수 있습니다:

1. **vLLM** (기본값)
   - 로컬 서버에서 실행되는 오픈소스 모델 사용
   - .env 파일에 `MODEL_API_KEY`와 `MODEL_API_URL` 설정 필요

2. **Gemini** 
   - Google의 Gemini 모델 사용
   - Google API 키 입력 필요

### 🔍 검색 엔진 선택  
사이드바에서 웹 검색에 사용할 엔진을 선택할 수 있습니다:

1. **Tavily** (기본값)
   - 전문적인 AI 검색 API
   - 환경변수 또는 직접 API 키 입력

2. **Google**
   - Google Search grounding을 통한 실시간 웹 검색
   - Gemini API의 Google Search 기능 사용
   - Google API 키만 필요 (CSE ID 불필요)

## 설정 방법

### 환경 변수 (.env 파일)
```env
# vLLM 설정
MODEL_API_KEY=your_vllm_api_key
MODEL_API_URL=http://localhost:5532/v1

# Gemini 설정 (Google 검색용으로도 사용)
GEMINI_API_KEY=your_gemini_api_key

# Tavily 검색
TAVILY_API_KEY=your_tavily_api_key

# Google 검색
GOOGLE_API_KEY=your_google_api_key
```

### 사용자 인터페이스에서 직접 입력
환경변수에 설정하지 않은 API 키들은 사이드바에서 직접 입력할 수 있습니다:

- Gemini 선택 시 → Google API 키 입력 필드 표시
- Tavily 선택 시 → Tavily API 키 입력 필드 표시 (환경변수 없는 경우)
- Google 검색 선택 시 → Google API 키 입력 필드 표시

## 사용법

1. **설정 확인**: 사이드바에서 원하는 모델과 검색 엔진 선택
2. **API 키 입력**: 필요한 경우 해당 API 키들 입력
3. **검증**: "현재 설정" 섹션에서 모든 설정이 올바르게 되었는지 확인
4. **질문 입력**: 메인 화면에서 연구하고 싶은 주제 입력
5. **결과 확인**: AI가 선택된 모델과 검색 엔진을 사용하여 답변 생성

## 오류 해결

### 설정 오류 메시지가 나타나는 경우:
- 선택한 모델에 맞는 API 키가 입력되었는지 확인
- 선택한 검색 엔진에 필요한 모든 정보가 입력되었는지 확인
- 사이드바의 "현재 설정" 섹션에서 모든 항목이 "✅ 설정됨"으로 표시되는지 확인

### API 키 관련:
- **Gemini API 키**: [Google AI Studio](https://makersuite.google.com/app/apikey)에서 발급
- **Tavily API 키**: [Tavily 웹사이트](https://tavily.com/)에서 회원가입 후 발급
- **Google Search**: Google API 키만 있으면 Gemini의 Google Search grounding 기능 사용 가능

## 기술적 세부사항

### 모델 어댑터
- 런타임에 사용자 선택에 따라 적절한 모델 초기화
- vLLM과 Gemini 모델 간 자동 전환

### 검색 도구
- Tavily와 Google Search grounding 지원
- 검색 결과를 통일된 형식으로 변환
- 인용 정보 자동 추가

### 설정 검증
- 사용자 입력 전 모든 필수 API 키 확인
- 누락된 설정에 대한 명확한 오류 메시지 제공

## 주의사항

- Google 검색 기능은 Gemini의 Google Search grounding을 사용하며, Google API 키만 필요합니다
- 일부 API에는 사용량 제한이 있을 수 있습니다
- API 키는 보안상 브라우저 세션에만 저장되며, 새로고침 시 다시 입력해야 합니다

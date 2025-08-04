import os
import openai
from dotenv import load_dotenv

print("🔍 연결 진단 스크립트를 시작합니다...")

# .env 파일에서 환경 변수를 불러옵니다.
load_dotenv()

api_key = os.getenv("MODEL_API_KEY")
api_base_url = os.getenv("MODEL_API_URL")

if not api_base_url:
    print("❌ 에러: .env 파일에서 MODEL_API_URL을 찾을 수 없습니다!")
    exit()

print(f"✅ 환경 변수를 읽었습니다.")
print(f"   - API Base URL: {api_base_url}")
print(f"   - API Key: {'설정됨' if api_key else '설정되지 않음'}")
print("-" * 30)

try:
    print(f"🚀 '{api_base_url}' 주소로 연결을 시도합니다...")

    # 주인님의 에이전트와 동일한 설정으로 클라이언트를 생성합니다.
    client = openai.OpenAI(
        api_key=api_key,
        base_url=api_base_url,
    )

    # 간단한 API 호출을 통해 연결을 테스트합니다 (예: 모델 목록 가져오기)
    models = client.models.list()

    print("\n✅ 성공! 서버에 성공적으로 연결되었습니다.")
    print(f"   - 가져온 모델 수: {len(models.data)}개")

except openai.APIConnectionError as e:
    print("\n❌ 실패: APIConnectionError가 발생했습니다!")
    print("   - 에러의 원인은 다음과 같을 수 있습니다:")
    print("     1. 서버 주소(URL) 또는 포트가 잘못되었습니다.")
    print("     2. 로컬 서버인 경우, 서버가 현재 실행 중이 아닙니다.")
    print("     3. 'https://' 주소인 경우, SSL/TLS 인증서 문제일 수 있습니다.")
    print("\n상세 에러 내용:")
    print(e.__cause__)  # 에러의 근본 원인을 보여줍니다.

except Exception as e:
    print(f"\n❌ 실패: 예상치 못한 에러가 발생했습니다: {type(e).__name__}")
    print(e)

print("\n🔍 진단 스크립트를 종료합니다.")

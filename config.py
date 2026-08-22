import os

# python-dotenv를 쓰면 .env 파일에서 자동으로 환경 변수를 불러올 수 있음
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# API 키는 절대 코드에 직접 작성하지 않고 환경 변수에서 읽어온다.
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
IMAGE_API_KEY = os.getenv("IMAGE_API_KEY", OPENAI_API_KEY)  # 같은 provider면 기본값으로 재사용

DEFAULT_OUTPUT_DIR = "./output"

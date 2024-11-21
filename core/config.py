import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

class Config:
    
    # CORS
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "").split(",")

    # OpenAI
    OPENAI_KEY = os.getenv("OPENAI_KEY")

config = Config()

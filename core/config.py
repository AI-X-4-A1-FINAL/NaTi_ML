import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

class Config:
    # DB
    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = os.getenv("DB_PORT")
    DB_NAME = os.getenv("DB_NAME")
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    
    DATABASE_URL = f"mysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

    # CORS
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "").split(",")

    # OpenAI
    OPENAI_KEY = os.getenv("OPENAI_KEY")

config = Config()

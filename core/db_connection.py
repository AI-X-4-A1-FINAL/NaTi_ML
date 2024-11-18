from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from core.config import config

# 데이터베이스 연결 엔진 생성
engine = create_engine(config.DATABASE_URL)

# 세션 생성기
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 데이터베이스 연결 확인용 함수
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

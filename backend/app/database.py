# /app/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from app.config import settings

# 데이터베이스 엔진 생성
engine = create_engine(settings.DATABASE_URL)

# 데이터베이스 세션 생성을 위한 SessionLocal 클래스
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# SQLAlchemy 모델의 베이스 클래스
Base = declarative_base()

# 의존성 주입을 위한 DB 세션 제공 함수
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
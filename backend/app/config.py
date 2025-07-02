# /app/config.py
import os
from dotenv import load_dotenv

# .env 파일에서 환경변수 로드
load_dotenv()

class Settings:
    DB_HOST: str = os.getenv("DB_HOST")
    DB_PORT: int = int(os.getenv("DB_PORT", 3306))
    DB_USER: str = os.getenv("DB_USER")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD")
    DB_NAME: str = os.getenv("DB_NAME")
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY")

    # SQLAlchemy 데이터베이스 URL 생성
    @property
    def DATABASE_URL(self):
        return f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}?charset=utf8mb4"

settings = Settings()
# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import exams, feedback

app = FastAPI(
    title="해기사 시험 AI 솔루션 API",
    description="기출문제 조회 및 AI 피드백 제공",
    version="2.0.0"
)

# CORS 미들웨어 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 실제 배포 시에는 프론트엔드 주소로 제한
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 포함
app.include_router(exams.router)
app.include_router(feedback.router)

@app.get("/", tags=["Root"])
def read_root():
    return {"message": "해기사 시험 AI 솔루션 API에 오신 것을 환영합니다."}
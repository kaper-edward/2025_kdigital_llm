# /app/routers/exams.py
from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.orm import Session
from app import crud, schemas
from app.database import get_db

router = APIRouter(
    prefix="/exams",
    tags=["Exams"],
)

@router.get("/{license_type}/{grade}/{year}/{inning}", response_model=schemas.ExamResponseSchema)
def read_exam(
    license_type: str = Path(..., description="자격증 종류 (예: 항해사)"),
    grade: str = Path(..., description="상세 급수 (예: 6급)"),
    year: int = Path(..., description="시행 연도 (예: 2023)"),
    inning: int = Path(..., description="회차 (예: 1)"),
    db: Session = Depends(get_db)
):
    """
    지정된 조건의 기출문제 전체 데이터를 조회합니다.
    """
    exam = crud.get_exam_by_details(db, license_type=license_type, grade=grade, year=year, inning=inning)
    if exam is None:
        raise HTTPException(status_code=404, detail="해당 시험 데이터를 찾을 수 없습니다.")
    return exam
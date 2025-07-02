# /app/crud.py
from sqlalchemy.orm import Session
from . import models, schemas
from typing import List

def get_exam_by_details(db: Session, license_type: str, grade: str, year: int, inning: int):
    """
    시험 상세 정보를 기반으로 DB에서 시험 데이터를 조회하고,
    프론트엔드 형식에 맞게 재구성합니다.
    """
    exam = db.query(models.Exam).filter(
        models.Exam.license_type == license_type,
        models.Exam.grade == grade,
        models.Exam.year == year,
        models.Exam.inning == inning
    ).first()

    if not exam:
        return None

    # 프론트엔드가 요구하는 중첩된 JSON 구조로 재구성
    subjects_list = []
    for subject in exam.subjects:
        questions_list = [
            schemas.QuestionSchema.from_orm(q) for q in subject.questions
        ]
        subjects_list.append(
            schemas.SubjectSchema(name=subject.name, questions=questions_list)
        )

    exam_detail = schemas.ExamDetailSchema(
        grade=exam.grade,
        year=exam.year,
        inning=exam.inning,
        type=subjects_list
    )

    return schemas.ExamResponseSchema(subject=exam_detail)
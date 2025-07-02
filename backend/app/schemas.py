# /app/schemas.py
from pydantic import BaseModel, Field
from typing import List, Optional

# --- Question Schemas ---
class QuestionSchema(BaseModel):
    num: int = Field(..., alias='question_number')
    questionsStr: str = Field(..., alias='question_text')
    ex1Str: Optional[str] = Field(None, alias='option_a')
    ex2Str: Optional[str] = Field(None, alias='option_b')
    ex3Str: Optional[str] = Field(None, alias='option_c')
    ex4Str: Optional[str] = Field(None, alias='option_d')
    answer: str = Field(..., alias='correct_answer')
    image_ref: Optional[str] = None

    class Config:
        # [수정] orm_mode -> from_attributes
        from_attributes = True
        allow_population_by_field_name = True

# --- Subject Schemas ---
class SubjectSchema(BaseModel):
    string: str = Field(..., alias='name')
    questions: List[QuestionSchema]

    class Config:
        # [수정] orm_mode -> from_attributes
        from_attributes = True
        allow_population_by_field_name = True

# --- Exam Schemas (for response) ---
class ExamDetailSchema(BaseModel):
    name: str = Field(..., alias='grade')
    year: int
    inning: int
    type: List[SubjectSchema]

    class Config:
        # [수정] orm_mode -> from_attributes
        from_attributes = True
        allow_population_by_field_name = True

class ExamResponseSchema(BaseModel):
    subject: ExamDetailSchema

# --- Feedback Schemas (변경 없음) ---
# 이 스키마들은 ORM 객체에서 데이터를 읽어오지 않으므로 수정할 필요가 없습니다.
class FeedbackRequest(BaseModel):
    question: str
    user_answer: str
    correct_answer: str
    is_correct: bool

class FeedbackResponse(BaseModel):
    result: str
    explanation: str
    tip: str
    relatedConcepts: List[str]
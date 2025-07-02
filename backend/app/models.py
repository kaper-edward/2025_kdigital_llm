# /app/models.py
from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class Exam(Base):
    __tablename__ = "exams"
    id = Column(Integer, primary_key=True, index=True)
    license_type = Column(String(50), nullable=False)
    grade = Column(String(100), nullable=False)
    year = Column(Integer, nullable=False)
    inning = Column(Integer, nullable=False)
    subjects = relationship("Subject", back_populates="exam", cascade="all, delete-orphan")

class Subject(Base):
    __tablename__ = "subjects"
    id = Column(Integer, primary_key=True, index=True)
    exam_id = Column(Integer, ForeignKey("exams.id"))
    name = Column(String(100), nullable=False)
    exam = relationship("Exam", back_populates="subjects")
    questions = relationship("Question", back_populates="subject", cascade="all, delete-orphan")

class Question(Base):
    __tablename__ = "questions"
    id = Column(Integer, primary_key=True, index=True)
    subject_id = Column(Integer, ForeignKey("subjects.id"))
    question_number = Column(Integer, nullable=False)
    question_text = Column(Text, nullable=False)
    option_a = Column(Text)
    option_b = Column(Text)
    option_c = Column(Text)
    option_d = Column(Text)
    correct_answer = Column(String(10), nullable=False)
    image_ref = Column(String(255), nullable=True)
    subject = relationship("Subject", back_populates="questions")
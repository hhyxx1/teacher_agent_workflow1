from sqlalchemy import Column, String, DateTime, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from pydantic import BaseModel
from typing import List, Optional

Base = declarative_base()

class QARecord(Base):
    """问答记录模型"""
    __tablename__ = "qa_records"
    
    id = Column(String, primary_key=True, index=True)
    student_id = Column(String, ForeignKey("users.id"))
    question = Column(Text)
    answer = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

# Pydantic 模型用于 API 请求和响应
class QuestionRequest(BaseModel):
    student_id: str
    question: str

class QuestionResponse(BaseModel):
    answer: str
    matched_skill: Optional[str] = None
    success: bool = True
    error: Optional[str] = None

class SkillInfo(BaseModel):
    id: str
    name: str
    description: str
    tags: List[str]

from pydantic import BaseModel
from typing import List, Optional, Any

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

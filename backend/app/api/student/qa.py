from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List
from app.agents.qa_agent import answer_student_question
from app.models.qa import QuestionRequest as AgentQuestionRequest
from app.models.qa import QuestionResponse as AgentQuestionResponse

router = APIRouter()

# 请求/响应模型
class QuestionRequest(BaseModel):
    question: str

class QuestionResponse(BaseModel):
    answer: str
    question_id: str

class QAHistoryItem(BaseModel):
    id: str
    question: str
    answer: str
    timestamp: str

@router.post("/ask", response_model=QuestionResponse)
async def ask_question(request: QuestionRequest, student_id: str = Query(..., description="学生ID")):
    """
    学生提交问题，获取AI回答
    """
    try:
        # 使用新的 answer_student_question 函数处理学生提问
        result = answer_student_question(student_id, request.question)
        
        if result["success"]:
            return QuestionResponse(
                answer=result["answer"],
                question_id=f"qa_{student_id}_{hash(request.question) % 10000}"
            )
        else:
            return QuestionResponse(
                answer=f"抱歉，处理您的问题时出现了错误：{result.get('error', '未知错误')}",
                question_id=f"qa_{student_id}_{hash(request.question) % 10000}"
            )
    except Exception as e:
        return QuestionResponse(
            answer=f"抱歉，处理您的问题时出现了错误：{str(e)}",
            question_id=f"qa_{student_id}_{hash(request.question) % 10000}"
        )

@router.get("/history", response_model=List[QAHistoryItem])
async def get_history():
    """
    获取问答历史记录
    """
    # TODO: 从数据库获取历史记录
    return [
        QAHistoryItem(
            id="1",
            question="什么是React？",
            answer="React是一个用于构建用户界面的JavaScript库。",
            timestamp="2026-01-26T10:00:00"
        )
    ]

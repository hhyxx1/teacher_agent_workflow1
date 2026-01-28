from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List
from app.graph.workflow import create_qa_workflow
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
        # 使用新的统一工作流处理学生提问
        workflow = create_qa_workflow()
        
        # 准备初始状态
        initial_state = {
            "student_id": student_id,
            "skill_title": "",  # QA流程不需要特定技能
            "question": request.question,
            "matched_skills": [],
            "answer": "",
            "qa_result": {},
            "new_skill_generated": False,
            "generated_skill_title": "",
            "skill_content": "",
            "skill_metadata": {},
            "questions": [],
            "student_answers": [],
            "grading_result": {},
            "score_history": [],
            "analysis_report": {},
            "need_retry": False
        }
        
        # 执行工作流
        result = workflow.invoke(initial_state)
        
        # 处理工作流结果
        if result.get("qa_result", {}).get("success"):
            answer = result.get("answer", "")
            return QuestionResponse(
                answer=answer,
                question_id=f"qa_{student_id}_{hash(request.question) % 10000}"
            )
        else:
            error_message = result.get("qa_result", {}).get("error", "未知错误")
            return QuestionResponse(
                answer=f"抱歉，处理您的问题时出现了错误：{error_message}",
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

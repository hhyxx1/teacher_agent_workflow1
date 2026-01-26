from fastapi import APIRouter, HTTPException
from backend.app.models.qa import QuestionRequest, QuestionResponse
from backend.app.services.skill_service import SkillService
from backend.app.config import get_llm

router = APIRouter(prefix="/qa", tags=["QA"])
skill_service = SkillService()
@router.post("/ask", response_model=QuestionResponse)
async def ask_question(request: QuestionRequest):
    """
    学生提问接口：自动匹配 Skill 并生成回答
    """
    try:
        llm = get_llm()
        if not llm:
            raise ValueError("LLM 实例未初始化，请检查 API_KEY 配置。")
        
        # 1. 自动搜索匹配的 Skill
        matched_skill_id = skill_service.find_best_match(request.question)
        skill_context = ""
        
        if matched_skill_id:
            content = skill_service.get_skill_content(matched_skill_id)
            if content:
                skill_context = f"\n参考教学技能内容:\n{content}\n"

        # 2. 调用大模型生成回答
        prompt = f"""
你是一个专业的课程老师。请结合提供的教学技能（如果有）回答学生的问题。
如果问题与教学技能相关，请尽量引用技能中的教学思路。

{skill_context}

学生提问: {request.question}

回答要求：
1. 语气亲切、专业。
2. 如果引用了教学技能，请在回答中适当提及。
3. 解释要通俗易懂。
"""
        response = llm.invoke(prompt)
        
        return QuestionResponse(
            answer=response.content,
            matched_skill=matched_skill_id,
            success=True
        )
    except Exception as e:
        return QuestionResponse(
            answer="抱歉，处理您的问题时出现了错误。",
            success=False,
            error=str(e)
        )

@router.get("/skills")
async def list_skills():
    """获取系统内所有可用的教学技能列表"""
    return skill_service.list_available_skills()

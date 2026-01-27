"""
出题 Agent (Question Generation Agent)

职责：
    根据给定的教学技能 (Skill) 内容，利用 LLM 生成高质量、符合要求的自测题目。

Prompt 设计策略：
    1. 角色设定：专业出题教师，语气严谨。
    2. 结构化约束：通过 system prompt 强制要求输出 JSON 数组，包含固定的字段名。
    3. 多样化要求：要求题型混合（单选、填空、简答），难度以基础为主。
"""

from langchain_core.prompts import ChatPromptTemplate
from app.config import get_llm
import json

# =================================================================
# 1. Prompt 模板定义
# =================================================================
prompt = ChatPromptTemplate.from_messages([
    ("system", """
你是专业出题教师，根据给定的Skill内容，生成{num}道自测题。
要求：
1. 题型：单选、填空、简答混合。单选题必须提供 options 列表。
2. 难度分布：70% 基础，20% 进阶，10% 挑战。
3. 字段要求：每题必须包含以下字段：
   - id: 题目编号 (1, 2, 3...)
   - type: 题型 ("choice", "fill", "essay")
   - question: 题目正文
   - options: 选项列表 (仅限 choice 题型，否则为空数组)
   - answer: 标准答案
   - difficulty: 难度等级 ("easy", "medium", "hard")
4. 输出格式：必须输出纯 JSON 数组，不要包含任何 Markdown 标签或解释性文字。
"""),
    ("user", "Skill标题：{title}\nSkill内容：{content}\n请为学生生成 {num} 道题目。")
])

def generate_daily_questions(skill_content: str, skill_metadata: dict, student_id: str, num_questions: int = 5) -> list[dict]:
    """
    核心出题函数
    
    Args:
        skill_content (str): Skill 的核心教学内容正文。
        skill_metadata (dict): Skill 的元数据，通常包含 "技能描述" 等字段。
        student_id (str): 学生 ID，用于后续可能的个性化调整（当前版本主要用于日志记录）。
        num_questions (int): 期望生成的题目总数。
        
    Returns:
        list[dict]: 题目字典列表。如果 LLM 失败或 JSON 解析错误，返回空列表。
    """
    llm = get_llm()
    if not llm:
        print("错误：LLM 实例未初始化，请检查 API_KEY 配置。")
        return []
        
    # 构建 LangChain 处理链
    chain = prompt | llm
    
    # 执行生成
    try:
        resp = chain.invoke({
            "title": skill_metadata.get("技能描述", "未命名技能"),
            "content": skill_content,
            "num": num_questions
        })
        
        # 结果清洗：有时 LLM 会多给一些空格或换行，json.loads 前进行处理
        raw_content = resp.content.strip()
        
        # 处理 LLM 偶尔返回的 Markdown 代码块标签
        if raw_content.startswith("```json"):
            raw_content = raw_content[7:-3].strip()
        elif raw_content.startswith("```"):
            raw_content = raw_content[3:-3].strip()
            
        return json.loads(raw_content)
        
    except json.JSONDecodeError as je:
        print(f"JSON 解析失败：LLM 返回内容格式不正确。错误信息：{je}")
        return []
    except Exception as e:
        print(f"出题过程中发生未知错误: {e}")
        return []

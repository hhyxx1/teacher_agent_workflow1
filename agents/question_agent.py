from langchain.prompts import ChatPromptTemplate
from config import llm
import json

prompt = ChatPromptTemplate.from_messages([
    ("system", """
你是专业出题教师，根据给定的Skill内容，生成{num}道自测题。
要求：
1. 题型：单选、填空、简答混合
2. 难度：基础为主，少量进阶
3. 每题含：id、type、question、options（单选）、answer、difficulty
4. 输出严格JSON数组，不要其他文字
"""),
    ("user", "Skill标题：{title}\nSkill内容：{content}\n生成{num}题")
])

chain = prompt | llm

def generate_daily_questions(skill_content: str, skill_metadata: dict, student_id: str, num_questions: int = 5) -> list[dict]:
    resp = chain.invoke({
        "title": skill_metadata.get("技能描述", ""),
        "content": skill_content,
        "num": num_questions
    })
    try:
        return json.loads(resp.content)
    except:
        return []
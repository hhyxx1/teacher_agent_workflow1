from langchain.prompts import ChatPromptTemplate
from config import llm
import json

prompt = ChatPromptTemplate.from_messages([
    ("system", """
你是评分教师，对学生答案逐题评分，输出JSON：
{
  "total_score": 0-100,
  "details": [{"qid":1, "score":0-20, "correct_answer":"...", "feedback":"..."}],
  "weak_points": ["知识点1", "知识点2"],
  "overall_feedback": "..."
}
每题满分20，{num}题总分100。
"""),
    ("user", "题目：{questions}\n学生答案：{answers}")
])

chain = prompt | llm

def grade_answers(questions: list[dict], student_answers: list[str]) -> dict:
    q_str = json.dumps(questions, ensure_ascii=False)
    a_str = json.dumps(student_answers, ensure_ascii=False)
    resp = chain.invoke({
        "questions": q_str,
        "answers": a_str,
        "num": len(questions)
    })
    try:
        return json.loads(resp.content)
    except:
        return {"total_score": 0, "details": [], "weak_points": [], "overall_feedback": "评分失败"}
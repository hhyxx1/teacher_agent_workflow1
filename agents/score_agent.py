"""
评分 Agent (Grading Agent)

职责：
    模拟教师对学生提交的答案进行自动评分。
    不仅给出分数，还需提供详细的错题解析、知识点薄弱项分析以及整体的学习建议。

Prompt 设计策略：
    1. 输入：接收完整的题目列表和学生答案列表（JSON 字符串格式）。
    2. 输出约束：强制输出复杂的嵌套 JSON 结构，包含总分、每题详情、薄弱点列表等。
    3. 评分标准：在 System Prompt 中内嵌了评分准则（每题满分 20）。
"""

from langchain_core.prompts import ChatPromptTemplate
from config import get_llm
import json

# =================================================================
# 1. Prompt 模板定义
# =================================================================
prompt = ChatPromptTemplate.from_messages([
    ("system", """
你是评分教师，对学生答案逐题评分。

评分标准：
- 每题满分 20 分，{num} 题总分 100 分。
- 客观题（单选）错误得 0 分。
- 主观题（简答）根据关键词命中率给分。

请输出严格的 JSON 格式结果：
{{
  "total_score": <int, 0-100>,
  "details": [
    {{
      "qid": <int>,
      "score": <int, 0-20>,
      "is_correct": <bool>,
      "correct_answer": "<标准答案>",
      "feedback": "<简短评语，指出错误原因>"
    }}
  ],
  "weak_points": ["<薄弱知识点1>", "<薄弱知识点2>"],
  "overall_feedback": "<整体评价与建议>"
}}
"""),
    ("user", "【题目数据】：\n{questions}\n\n【学生作答】：\n{answers}")
])

def grade_answers(questions: list[dict], student_answers: list[str]) -> dict:
    """
    执行评分任务
    
    Args:
        questions (list[dict]): 原始题目列表（包含标准答案）。
        student_answers (list[str]): 学生的作答列表（顺序应与题目一致）。
        
    Returns:
        dict: 包含总分、详情、薄弱点和整体反馈的字典。
              如果发生错误，返回带有错误信息的默认字典，确保工作流不中断。
    """
    llm = get_llm()
    if not llm:
        print("错误：LLM 实例未初始化。")
        return {"total_score": 0, "details": [], "weak_points": [], "overall_feedback": "系统错误：评分服务不可用"}
        
    chain = prompt | llm
    
    # 序列化题目和答案，以避免 Prompt 注入风险并保持格式清晰
    q_str = json.dumps(questions, ensure_ascii=False)
    a_str = json.dumps(student_answers, ensure_ascii=False)
    
    try:
        resp = chain.invoke({
            "questions": q_str,
            "answers": a_str,
            "num": len(questions)
        })
        
        # 结果清洗
        raw_content = resp.content.strip()
        if raw_content.startswith("```json"):
            raw_content = raw_content[7:-3].strip()
        elif raw_content.startswith("```"):
            raw_content = raw_content[3:-3].strip()
            
        return json.loads(raw_content)
        
    except json.JSONDecodeError as je:
        print(f"JSON 解析失败：{je}")
        return {
            "total_score": 0, 
            "details": [], 
            "weak_points": [], 
            "overall_feedback": "评分解析失败，请检查模型输出格式。"
        }
    except Exception as e:
        print(f"评分过程中发生未知错误: {e}")
        return {
            "total_score": 0, 
            "details": [], 
            "weak_points": [], 
            "overall_feedback": "评分过程发生未知错误。"
        }
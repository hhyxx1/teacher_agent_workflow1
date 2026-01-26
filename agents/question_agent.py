# agents/question_agent.py
def generate_daily_questions(
    skill_content: str,
    skill_metadata: dict,
    student_id: str,
    num_questions: int = 5
) -> list[dict]:
    """
    输入：Skill内容+元数据、学生ID、题目数
    输出：题目列表（含id、type、question、options、answer、difficulty）
    """
    pass

# agents/score_agent.py
def grade_answers(
    questions: list[dict],
    student_answers: list[str]
) -> dict:
    """
    输入：题目列表 + 学生答案列表
    输出：评分结果（总分、每题得分、错题列表、评语）
    """
    pass


from typing import TypedDict

class WorkflowState(TypedDict):
    student_id: str
    skill_title: str
    skill_content: str
    skill_metadata: dict
    today_questions: list[dict]
    student_answers: list[str]
    score_result: dict
    score_history: list[dict]  # 历史分数
    progress_report: dict      # 进步评估
    need_retry: bool           # 是否需要复测
    done: bool                # 今日完成

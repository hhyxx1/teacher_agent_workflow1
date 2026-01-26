from typing import TypedDict, List, Dict

class WorkflowState(TypedDict):
    student_id: str
    skill_title: str
    skill_content: str
    skill_metadata: Dict
    today_questions: List[Dict]
    student_answers: List[str]
    score_result: Dict
    score_history: List[Dict]
    progress_report: Dict
    need_retry: bool
    done: bool
from graph.workflow import build_workflow
from config import NUM_QUESTIONS_PER_DAY

def run_daily_workflow(student_id: str, skill_title: str):
    app = build_workflow()
    initial_state = {
        "student_id": student_id,
        "skill_title": skill_title,
        "skill_content": "",
        "skill_metadata": {},
        "today_questions": [],
        "student_answers": [],
        "score_result": {},
        "score_history": [],
        "progress_report": {},
        "need_retry": False,
        "done": False
    }
    result = app.invoke(initial_state)
    return result

if __name__ == "__main__":
    # 运行示例
    student_id = "student_001"
    skill_title = "同步与互斥教学案例"
    final_state = run_daily_workflow(student_id, skill_title)

    print("="*50)
    print("今日总分：", final_state["score_result"]["total_score"])
    print("进步报告：", final_state["progress_report"])
    print("是否需要复测：", final_state["need_retry"])
    print("="*50)
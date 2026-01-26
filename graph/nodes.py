from utils.skill_loader import load_skill
from utils.data_manager import save_daily_questions, load_daily_questions, save_score, load_score_history
from utils.progress_analyzer import analyze_progress
from agents.question_agent import generate_daily_questions
from agents.score_agent import grade_answers
from config import NUM_QUESTIONS_PER_DAY, RETRY_THRESHOLD
from graph.state import WorkflowState

# 节点1：加载Skill
def load_skill_node(state: WorkflowState) -> WorkflowState:
    skill = load_skill(state["skill_title"])
    return {
        **state,
        "skill_content": skill["content"],
        "skill_metadata": skill["metadata"]
    }

# 节点2：生成今日题目
def generate_questions_node(state: WorkflowState) -> WorkflowState:
    # 若今天已生成，直接加载
    existing = load_daily_questions(state["student_id"])
    if existing:
        return {**state, "today_questions": existing}
    
    questions = generate_daily_questions(
        skill_content=state["skill_content"],
        skill_metadata=state["skill_metadata"],
        student_id=state["student_id"],
        num_questions=NUM_QUESTIONS_PER_DAY
    )
    save_daily_questions(state["student_id"], questions)
    return {**state, "today_questions": questions}

# 节点3：模拟学生答题（实际可替换为前端输入）
def simulate_answer_node(state: WorkflowState) -> WorkflowState:
    # 这里模拟：随机答，实际由学生输入
    answers = [q.get("answer", "") for q in state["today_questions"]]
    return {**state, "student_answers": answers}

# 节点4：评分
def grade_node(state: WorkflowState) -> WorkflowState:
    score_result = grade_answers(state["today_questions"], state["student_answers"])
    return {**state, "score_result": score_result}

# 节点5：保存分数 & 加载历史
def save_score_node(state: WorkflowState) -> WorkflowState:
    save_score(
        student_id=state["student_id"],
        score_result=state["score_result"],
        skill_title=state["skill_title"]
    )
    history = load_score_history(state["student_id"])
    return {**state, "score_history": history}

# 节点6：进步评估
def analyze_progress_node(state: WorkflowState) -> WorkflowState:
    report = analyze_progress(state["score_history"], state["skill_title"])
    return {**state, "progress_report": report}

# 节点7：判断是否需要复测 & 结束
def decide_retry_node(state: WorkflowState) -> WorkflowState:
    total = state["score_result"]["total_score"]
    need_retry = total < RETRY_THRESHOLD
    done = not need_retry
    return {**state, "need_retry": need_retry, "done": done}
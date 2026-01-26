"""
工作流节点定义 (Workflow Nodes)

本模块包含了 LangGraph 工作流中的所有业务逻辑节点。
每个节点都是一个纯函数，接收当前状态 (state)，执行操作，并返回更新后的状态。

设计原则：
1. 职责单一：每个节点只负责一个核心任务（如：只加载、只评分）。
2. 状态驱动：通过更新 WorkflowState 中的字段来驱动后续节点的执行。
3. 可持久化：在关键节点（出题、评分）自动触发本地文件保存。
"""

from .state import WorkflowState
from utils.skill_loader import load_skill
from utils.data_manager import save_daily_questions, load_daily_questions, save_score, load_score_history
from utils.progress_analyzer import analyze_progress
from agents.question_agent import generate_daily_questions
from agents.score_agent import grade_answers
from config import NUM_QUESTIONS_PER_DAY, RETRY_THRESHOLD

def load_skill_node(state: WorkflowState) -> WorkflowState:
    """
    [节点 1: 加载技能]
    
    前置条件: state["skill_title"] 必须存在且对应 skills/ 目录下的有效 .md 文件。
    操作: 调用 skill_loader 解析 Markdown 文件的元数据和教学内容。
    后置条件: 填充 skill_content 和 skill_metadata。
    """
    print(f"--- 正在加载 Skill: {state['skill_title']} ---")
    skill_data = load_skill(state["skill_title"])
    return {
        **state,
        "skill_content": skill_data["content"],
        "skill_metadata": skill_data["metadata"]
    }

def generate_questions_node(state: WorkflowState) -> WorkflowState:
    """
    [节点 2: 生成题目]
    
    前置条件: 已成功加载技能内容。
    操作: 
        1. 优先尝试从本地 data/questions/ 缓存加载今日题目。
        2. 若无缓存，则调用 Question Agent 通过 LLM 生成新题目。
    后置条件: 填充 questions 列表，并确保题目已持久化到本地。
    """
    print(f"--- 正在为学生 {state['student_id']} 生成/加载题目 ---")
    
    # 缓存检查：避免在同一天内重复调用 LLM
    existing = load_daily_questions(state["student_id"])
    if existing:
        print("   (从本地缓存加载了今日题目)")
        return {**state, "questions": existing}
    
    # 调用 LLM 生成
    questions = generate_daily_questions(
        skill_content=state["skill_content"],
        skill_metadata=state["skill_metadata"],
        student_id=state["student_id"],
        num_questions=NUM_QUESTIONS_PER_DAY
    )
    
    # 持久化存储
    save_daily_questions(state["student_id"], questions)
    return {**state, "questions": questions}

def grade_answers_node(state: WorkflowState) -> WorkflowState:
    """
    [节点 3: 评分与持久化]
    
    前置条件: state["questions"] 和 state["student_answers"] 已就绪。
    操作: 
        1. 调用 Score Agent 对答案进行评分。
        2. 将得分记录、薄弱点等信息追加保存到 data/scores/ 的 JSONL 文件中。
    后置条件: 填充 grading_result。
    """
    print(f"--- 正在评分并记录成绩 ---")
    result = grade_answers(state["questions"], state["student_answers"])
    
    # 保存单次得分记录，用于后续分析
    save_score(
        student_id=state["student_id"],
        score_result=result,
        skill_title=state["skill_title"]
    )
    return {**state, "grading_result": result}

def simulate_student_input_node(state: WorkflowState) -> WorkflowState:
    """
    [模拟节点: 学生答题]
    
    注意: 在实际生产环境中，此节点通常会被替换为等待 Web 前端回调或命令行输入的逻辑。
    操作: 遍历题目，自动提取标准答案作为学生的“完美”输入。
    """
    print(f"--- [模拟] 学生正在答题... ---")
    # 模拟完美答题：直接拿正确答案填充
    answers = [q.get("answer", "") for q in state["questions"]]
    return {**state, "student_answers": answers}

def analyze_progress_node(state: WorkflowState) -> WorkflowState:
    """
    [节点 4: 进度评估]
    
    前置条件: 当前评分已完成。
    操作: 
        1. 从本地加载该学生的所有历史成绩记录。
        2. 调用分析器对比当前表现与历史表现，识别进步趋势。
    后置条件: 填充 score_history 和 analysis_report。
    """
    print(f"--- 正在进行多维度进度分析 ---")
    history = load_score_history(state["student_id"])
    report = analyze_progress(history, state["skill_title"])
    return {
        **state, 
        "score_history": history,
        "analysis_report": report
    }

def decide_retry_node(state: WorkflowState) -> WorkflowState:
    """
    [节点 5: 逻辑决策]
    
    前置条件: 评分结果已产生。
    操作: 检查总分是否低于 config.RETRY_THRESHOLD (默认 50 分)。
    后置条件: 填充 need_retry 标志位，控制工作流是走向 END 还是返回 generate_questions。
    """
    total = state["grading_result"].get("total_score", 0)
    need_retry = total < RETRY_THRESHOLD
    
    if need_retry:
        print(f"--- 分数过低 ({total} < {RETRY_THRESHOLD})，标记为需要复测 ---")
    else:
        print(f"--- 表现优秀 ({total} >= {RETRY_THRESHOLD})，课程任务完成 ---")
        
    return {**state, "need_retry": need_retry}
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
from app.utils.skill_manager import load_skill, search_skills, create_skill, get_skill_detail, get_skill_template, list_skills
from app.utils.data_manager import save_daily_questions, load_daily_questions, save_score, load_score_history
from app.utils.progress_analyzer import analyze_progress
from app.agents.question_agent import generate_daily_questions
from app.agents.score_agent import grade_answers
from app.config.settings import settings
from app.config import get_llm
from langchain_core.prompts import ChatPromptTemplate

def load_skill_node(state: WorkflowState) -> WorkflowState:
    """
    [节点 1: 加载技能]
    
    前置条件: state["skill_title"] 必须存在。
    操作: 从本地 skills/ 目录加载对应的 Markdown 文件。
    后置条件: 填充 skill_content 和 skill_metadata。
    """
    skill_title = state['skill_title']
    print(f"--- 正在加载 Skill: {skill_title} ---")
    
    skill_data = load_skill(skill_title)

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
        num_questions=settings.NUM_QUESTIONS_PER_DAY
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
    score_record = {
        "student_id": state["student_id"],
        "skill": state["skill_title"],
        "score": result["total_score"],
        "weak_points": result["weak_points"],
        "feedback": result["overall_feedback"]
    }
    save_score(score_record)
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
    need_retry = total < settings.RETRY_THRESHOLD
    
    if need_retry:
        print(f"--- 分数过低 ({total} < {settings.RETRY_THRESHOLD})，标记为需要复测 ---")
    else:
        print(f"--- 表现优秀 ({total} >= {settings.RETRY_THRESHOLD})，课程任务完成 ---")
        
    return {**state, "need_retry": need_retry}


def match_skill_node(state: WorkflowState) -> WorkflowState:
    """
    [QA节点 1: 匹配技能]
    
    前置条件: state["question"] 必须存在。
    操作: 根据学生问题搜索匹配的Skill。
    后置条件: 填充 matched_skills 列表。
    """
    question = state['question']
    print(f"--- 正在为问题匹配相关Skill: {question[:50]}... ---")
    
    matched_skills = search_skills(question)
    print(f"--- 找到 {len(matched_skills)} 个匹配的Skill ---")
    
    return {
        **state,
        "matched_skills": matched_skills
    }


def generate_skill_node(state: WorkflowState) -> WorkflowState:
    """
    [QA节点 2: 生成技能]
    
    前置条件: state["question"] 存在且 state["matched_skills"] 为空。
    操作: 基于学生问题和现有Skill生成新的Skill。
    后置条件: 填充 new_skill_generated 和 generated_skill_title。
    """
    question = state['question']
    print(f"--- 未找到匹配Skill，正在生成新Skill... ---")
    
    # 获取所有现有Skill作为上下文
    all_skills = list_skills()
    existing_content = ""
    
    if all_skills:
        # 取前5个相关Skill作为上下文（避免token过多）
        for skill in all_skills[:5]:
            skill_detail = get_skill_detail(skill.get("标题"))
            if skill_detail:
                existing_content += f"## {skill_detail['title']}\n"
                existing_content += f"描述：{skill_detail['metadata'].get('技能描述', '')}\n"
                existing_content += f"内容：{skill_detail['content'][:500]}...\n\n"
    
    # 使用LLM生成新Skill
    llm = get_llm()
    prompt = ChatPromptTemplate.from_messages([
        ("system", """
你是一个专业的教学助手，需要基于学生的问题和现有教学Skill，创建一个新的教学Skill。

要求：
1. 新Skill必须使用标准的MD格式
2. 包含技能描述、适用场景、核心内容
3. 确保内容准确、有教学价值
4. 如果现有Skill相关，要整合相关知识
5. 生成的Skill标题要简洁明了
"""),
        ("user", """
学生问题：{question}

现有相关教学Skill：
{existing_skills}

请基于以上信息，生成一个新的教学Skill，使用以下模板：

{template}

请填充模板内容，生成完整的Skill MD文本。
""")
    ])
    
    chain = prompt | llm
    
    # 获取Claude风格模板
    template = get_skill_template("claude")
    
    try:
        response = chain.invoke({
            "question": question,
            "existing_skills": existing_content or "暂无相关Skill",
            "template": template
        })
        
        # 解析生成的Skill内容
        generated_content = response.content.strip()
        
        # 提取标题（从第一行#开始）
        lines = generated_content.split('\n')
        title = ""
        for line in lines:
            if line.startswith('# '):
                title = line[2:].strip()
                break
        
        if not title:
            return {
                **state,
                "new_skill_generated": False,
                "qa_result": {
                    "success": False,
                    "error": "无法从生成内容中提取Skill标题"
                }
            }
        
        # 创建新Skill
        create_result = create_skill(title, generated_content)
        
        if create_result["success"]:
            print(f"--- 新Skill生成成功: {title} ---")
            return {
                **state,
                "new_skill_generated": True,
                "generated_skill_title": title
            }
        else:
            return {
                **state,
                "new_skill_generated": False,
                "qa_result": {
                    "success": False,
                    "error": create_result.get("errors", ["创建Skill失败"])
                }
            }
    except Exception as e:
        return {
            **state,
            "new_skill_generated": False,
            "qa_result": {
                "success": False,
                "error": f"生成新Skill时出错: {str(e)}"
            }
        }


def generate_answer_node(state: WorkflowState) -> WorkflowState:
    """
    [QA节点 3: 生成回答]
    
    前置条件: state["question"] 和 state["matched_skills"] 存在。
    操作: 基于匹配的Skill内容生成学生问题的回答。
    后置条件: 填充 answer 和 qa_result。
    """
    question = state['question']
    matched_skills = state['matched_skills']
    print(f"--- 正在基于匹配的Skill生成回答... ---")
    
    # 准备Skill内容
    skill_content_list = []
    
    # 调用get_skill_detail获取技能详情
    for skill in matched_skills:
        detail = get_skill_detail(skill.get("标题"))
        if detail:
            skill_content_list.append({
                "title": detail["title"],
                "description": detail["metadata"].get("技能描述", ""),
                "content": detail["content"][:1000]  # 截取前1000字避免token过多
            })
    
    if not skill_content_list:
        return {
            **state,
            "qa_result": {
                "success": False,
                "error": "未找到相关Skill"
            }
        }
    
    # 使用LLM生成回答
    llm = get_llm()
    prompt = ChatPromptTemplate.from_messages([
        ("system", """
你是一名经验丰富的教师助手。根据给定的教学Skill内容，回答学生的问题。

要求：
1. 使用Skill中的知识、案例、原理来回答
2. 清晰、循序渐进地讲解
3. 必要时举例说明
4. 如果问题与Skill不完全相关，说明这一点
5. 在回答末尾列出参考的内容来源
"""),
        ("user", """
学生问题：{question}

相关教学Skill：
{skill_content}

请基于上述Skill内容，回答学生的问题。
""")
    ])

    chain = prompt | llm

    # 格式化Skill内容
    formatted_skills = "\n\n".join([
        f"【Skill: {s['title']}】\n描述：{s['description']}\n内容预览：{s['content']}"
        for s in skill_content_list
    ])

    try:
        response = chain.invoke({
            "question": question,
            "skill_content": formatted_skills
        })

        answer = response.content
        print(f"--- 回答生成成功 ---")
        
        return {
            **state,
            "answer": answer,
            "qa_result": {
                "success": True,
                "answer": answer,
                "matched_skills": [
                    {
                        "title": s.get("标题"),
                        "type": s.get("技能类型"),
                        "score": s.get("_match_score", 0)
                    }
                    for s in matched_skills
                ]
            }
        }
    except Exception as e:
        return {
            **state,
            "qa_result": {
                "success": False,
                "error": str(e)
            }
        }


def process_qa_node(state: WorkflowState) -> WorkflowState:
    """
    [QA节点 4: 处理完整QA流程]
    
    前置条件: state["question"] 存在。
    操作: 整合技能匹配、生成和回答生成的完整流程。
    后置条件: 填充完整的QA结果。
    """
    print(f"--- 开始处理学生问答流程 ---")
    
    # 1. 匹配技能
    state_with_matched = match_skill_node(state)
    matched_skills = state_with_matched['matched_skills']
    
    # 2. 如果没有匹配的技能，生成新技能
    if not matched_skills:
        state_with_generated = generate_skill_node(state_with_matched)
        
        if state_with_generated['new_skill_generated']:
            # 重新匹配技能
            question = state_with_generated['question']
            new_matched_skills = search_skills(question)
            
            if new_matched_skills:
                state_with_generated['matched_skills'] = new_matched_skills
            else:
                # 如果还是找不到，手动构建匹配技能
                state_with_generated['matched_skills'] = [{
                    "标题": state_with_generated['generated_skill_title'],
                    "技能描述": "AI自动生成的教学Skill",
                    "关键词": question.replace(" ", ",").split(",")[:3],
                    "技能类型": "授课",
                    "适用场景": f"回答问题：{question[:50]}...",
                    "难度等级": "中级",
                    "_match_score": 8.0,
                    "_match_details": ["AI自动生成"]
                }]
        else:
            # 生成失败，返回错误
            return state_with_generated
    else:
        state_with_generated = state_with_matched
    
    # 3. 生成回答
    state_with_answer = generate_answer_node(state_with_generated)
    
    print(f"--- 学生问答流程处理完成 ---")
    return state_with_answer

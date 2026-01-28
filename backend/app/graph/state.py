"""
工作流状态定义 (Workflow State Definition)

该模块定义了 LangGraph 工作流中传递的核心数据结构。
使用 TypedDict 确保在各个节点函数之间传递数据时具有明确的类型约束。
"""

from typing import TypedDict, List, Dict

class WorkflowState(TypedDict):
    """
    LangGraph 工作流的状态容器
    
    属性说明：
        student_id (str): 学生的唯一标识符，用于检索历史成绩 and 保存题目。
        skill_title (str): 本次学习任务的目标 Skill 文件名。
        
        # QA相关
        question: str  # 学生的提问内容
        matched_skills: List[dict]  # 匹配的技能列表
        answer: str  # 生成的回答
        qa_result: dict  # QA处理的完整结果
        new_skill_generated: bool  # 是否生成了新技能
        generated_skill_title: str  # 生成的技能标题
        
        # 内容数据
        skill_content: str  # [由 load_skill_node 填充] 从 Markdown 加载的教学正文。
        skill_metadata: dict  # [由 load_skill_node 填充] 从 Markdown 加载的元数据（描述、难度等）。
        
        # 题目与答案
        questions: List[dict]  # [由 generate_questions_node 填充] LLM 生成的题目对象列表。
        student_answers: List[str]  # [由外部输入/模拟填充] 学生的原始答案文本。
        
        # 评分与分析
        grading_result: dict  # [由 grade_answers_node 填充] LLM 评分后的结果（总分、建议、薄弱项）。
        score_history: List[dict]  # [由 analyze_progress_node 填充] 从本地加载的学生历史成绩记录。
        analysis_report: dict  # [由 analyze_progress_node 填充] 包含进步趋势和学习建议的分析报告。
        
        # 流程控制
        need_retry: bool  # [由 decide_retry_node 填充] 控制流标志。如果分太低，设为 True 以触发循环。
    """
    # 基础信息
    student_id: str
    skill_title: str
    
    # QA相关
    question: str
    matched_skills: List[dict]
    answer: str
    qa_result: dict
    new_skill_generated: bool
    generated_skill_title: str
    
    # 内容数据
    skill_content: str
    skill_metadata: dict
    
    # 题目与答案
    questions: List[dict]
    student_answers: List[str]
    
    # 评分与分析
    grading_result: dict
    score_history: List[dict]
    analysis_report: dict
    
    # 流程控制
    need_retry: bool

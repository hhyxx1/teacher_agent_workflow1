"""
工作流编排模块 (Workflow Orchestration)

使用 LangGraph 构建教学任务的状态机。
该工作流定义了从“加载课程”到“出题”、“答题”、“评分”、“分析”并根据表现决定是否“重学”的完整循环。

图形结构：
    START -> load_skill -> generate_questions -> grade_answers -> analyze_progress -> decide_retry
    decide_retry -> END (如果达标)
    decide_retry -> generate_questions (如果不达标，触发复测循环)
"""

from langgraph.graph import StateGraph, START, END
from .state import WorkflowState
from .nodes import (
    load_skill_node, 
    generate_questions_node, 
    simulate_student_input_node, # 引入模拟节点
    grade_answers_node, 
    analyze_progress_node, 
    decide_retry_node
)

def create_workflow():
    """
    创建并编译 LangGraph 工作流
    
    Returns:
        CompiledGraph: 一个可执行的图对象，通过 invoke(initial_state) 启动。
    """
    # 1. 初始化状态图，指定状态结构类型
    workflow = StateGraph(WorkflowState)

    # 2. 注册所有节点函数
    # 节点名应简洁且具有描述性
    workflow.add_node("load_skill", load_skill_node)
    workflow.add_node("generate_questions", generate_questions_node)
    workflow.add_node("simulate_student_input", simulate_student_input_node) # 注册模拟节点
    workflow.add_node("grade_answers", grade_answers_node)
    workflow.add_node("analyze_progress", analyze_progress_node)
    workflow.add_node("decide_retry", decide_retry_node)

    # 3. 设置静态边 (Static Edges)
    # 这些步骤是顺序执行的，不依赖条件判断
    workflow.add_edge(START, "load_skill")
    workflow.add_edge("load_skill", "generate_questions")
    workflow.add_edge("generate_questions", "simulate_student_input") # 生成题目后模拟答题
    workflow.add_edge("simulate_student_input", "grade_answers")      # 答题后评分
    workflow.add_edge("grade_answers", "analyze_progress")
    workflow.add_edge("analyze_progress", "decide_retry")

    # 4. 设置条件边 (Conditional Edges)
    # 根据 decide_retry 节点的输出结果（need_retry 标志）决定下一步去向
    workflow.add_conditional_edges(
        "decide_retry",
        lambda state: "retry" if state.get("need_retry") else "end",
        {
            "retry": "generate_questions", # 分数低，重新回到出题环节
            "end": END                     # 任务完成
        }
    )

    # 5. 编译工作流
    # 编译后会进行循环检测和结构验证
    return workflow.compile()

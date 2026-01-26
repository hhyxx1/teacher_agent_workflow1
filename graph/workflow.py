from langgraph.graph import StateGraph, END
from graph.state import WorkflowState
from graph.nodes import (
    load_skill_node,
    generate_questions_node,
    simulate_answer_node,
    grade_node,
    save_score_node,
    analyze_progress_node,
    decide_retry_node
)

def build_workflow():
    workflow = StateGraph(WorkflowState)

    # 节点
    workflow.add_node("load_skill", load_skill_node)
    workflow.add_node("generate_questions", generate_questions_node)
    workflow.add_node("simulate_answer", simulate_answer_node)
    workflow.add_node("grade", grade_node)
    workflow.add_node("save_score", save_score_node)
    workflow.add_node("analyze_progress", analyze_progress_node)
    workflow.add_node("decide_retry", decide_retry_node)

    # 边
    workflow.set_entry_point("load_skill")
    workflow.add_edge("load_skill", "generate_questions")
    workflow.add_edge("generate_questions", "simulate_answer")
    workflow.add_edge("simulate_answer", "grade")
    workflow.add_edge("grade", "save_score")
    workflow.add_edge("save_score", "analyze_progress")
    workflow.add_edge("analyze_progress", "decide_retry")

    # 条件边：复测 or 结束
    workflow.add_conditional_edges(
        "decide_retry",
        lambda state: "retry" if state["need_retry"] else "end",
        {
            "retry": "generate_questions",  # 复测：重新出题
            "end": END
        }
    )

    return workflow.compile()
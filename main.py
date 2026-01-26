"""
智能助教工作流 - 主程序入口 (Main Entry Point)

该系统通过 LangGraph 编排多个 AI Agent，实现了一个闭环的自动化教学流程：
1. 课程加载：从本地 Markdown 文件读取教学大纲 (Skill)。
2. 个性化出题：根据 Skill 内容和学生历史，利用 LLM 生成针对性的自测题。
3. 答题模拟：模拟学生提交答案的过程（实际场景中可对接前端界面）。
4. 自动评分：利用 LLM 充当“数字老师”，对答案进行多维度评分和反馈。
5. 进度评估：对比历史成绩，分析学生的进步趋势，给出下一步学习建议。
6. 动态调整：如果得分不达标，自动触发“复测循环”，重新出题。

架构特点：
    - 状态驱动 (State-Driven): 所有节点共享 WorkflowState。
    - 持久化 (Persistence): 题目和成绩自动保存至本地 JSON/JSONL。
    - 模块化 (Modular): Agent、Graph、Utils 职责分明。
"""

from graph.workflow import create_workflow
from config import NUM_QUESTIONS_PER_DAY

def run_daily_workflow(student_id: str, skill_title: str):
    """
    运行每日学习工作流实例
    
    Args:
        student_id (str): 学生的唯一标识（如 "student_001"）。
        skill_title (str): 目标 Skill 的标题（需在 skills/ 目录下存在对应的 .md 文件）。
        
    Returns:
        dict: 工作流运行结束后的最终状态字典 (WorkflowState)。
    """
    # 1. 初始化工作流引擎
    # 编译过程会检查图结构的合法性（如循环引用、孤立节点等）
    app = create_workflow()
    
    # 2. 构造初始状态
    # 只需要提供必要的基础信息，后续数据将由各处理节点动态填充
    initial_state = {
        "student_id": student_id,
        "skill_title": skill_title,
        "skill_content": "",
        "skill_metadata": {},
        "questions": [],
        "student_answers": [],
        "grading_result": {},
        "score_history": [],
        "analysis_report": {},
        "need_retry": False
    }
    
    # 3. 启动执行
    # invoke 是同步阻塞调用，它会按照定义的边（Edges）依次执行各节点函数
    print(f"\n{'='*20} 工作流启动 {'='*20}")
    print(f"目标学生: {student_id}")
    print(f"目标技能: {skill_title}\n")
    
    final_state = app.invoke(initial_state)
    return final_state

if __name__ == "__main__":
    # =================================================================
    # 运行示例 (Execution Example)
    # =================================================================
    
    # 配置测试参数
    TEST_STUDENT = "student_001"
    TEST_SKILL = "同步与互斥教学案例" # 提示：请确保 skills/ 目录下有该文件
    
    try:
        # 执行工作流
        result = run_daily_workflow(TEST_STUDENT, TEST_SKILL)

        # 4. 最终结果展示
        print("\n" + "="*50)
        print("🎉 工作流执行任务完成！摘要信息如下：")
        print("-" * 50)
        
        # 提取评分结果
        grad_res = result.get("grading_result", {})
        score = grad_res.get("total_score", "N/A")
        feedback = grad_res.get("overall_feedback", "无评价")
        
        # 提取分析报告
        report = result.get("analysis_report", {})
        trend = report.get("trend_type", "数据不足")
        suggestion = report.get("suggestion", "继续保持")

        print(f"📝 本次测试得分: {score} 分")
        print(f"📈 进步趋势评估: {trend}")
        print(f"💡 学习专家建议: {suggestion}")
        print(f"🔄 是否触发复测: {'是 (请查阅新题目)' if result.get('need_retry') else '否 (已达标)'}")
        print("="*50 + "\n")

    except Exception as e:
        print(f"\n❌ 工作流运行失败: {e}")
        print("请检查：1. 是否配置了环境变量 API_KEY  2. skills/ 目录下文件是否存在\n")
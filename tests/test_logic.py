import sys
import os
import unittest
from unittest.mock import patch, MagicMock

# 将项目根目录添加到系统路径，以便导入模块
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from graph.workflow import create_workflow
from graph.state import WorkflowState

class TestWorkflowLogic(unittest.TestCase):
    """
    工作流逻辑测试类
    使用 Mock 技术模拟 LLM 响应，验证 LangGraph 状态机是否按预期流转。
    """

    def setUp(self):
        # 编译工作流应用
        self.app = create_workflow()
        self.student_id = "test_student_007"
        self.skill_title = "同步与互斥教学案例"

    @patch("agents.question_agent.generate_daily_questions")
    @patch("agents.score_agent.grade_answers")
    def test_full_workflow_flow(self, mock_grade, mock_gen):
        """测试完整工作流的成功路径"""
        
        # 1. 模拟 Question Agent 返回 2 道题
        mock_gen.return_value = [
            {"id": 1, "question": "什么是互斥？", "answer": "正确答案A"},
            {"id": 2, "question": "什么是同步？", "answer": "正确答案B"}
        ]

        # 2. 模拟 Score Agent 返回高分 (不触发复测)
        mock_grade.return_value = {
            "total_score": 90,
            "weak_points": ["无"],
            "overall_feedback": "表现完美"
        }

        # 3. 构造初始状态
        initial_state = {
            "student_id": self.student_id,
            "skill_title": self.skill_title,
            "skill_content": "",
            "skill_metadata": {},
            "questions": [],
            "student_answers": [],
            "grading_result": {},
            "score_history": [],
            "analysis_report": {},
            "need_retry": False
        }

        # 4. 执行工作流
        final_state = self.app.invoke(initial_state)

        # 5. 断言验证
        self.assertEqual(final_state["grading_result"]["total_score"], 90)
        self.assertFalse(final_state["need_retry"])
        self.assertTrue(len(final_state["questions"]) > 0)
        print("\n✅ 成功路径测试通过：工作流顺利结束，未触发复测。")

    @patch("agents.question_agent.generate_daily_questions")
    @patch("agents.score_agent.grade_answers")
    def test_retry_logic(self, mock_grade, mock_gen):
        """测试复测逻辑：低分时应标记 need_retry 为 True"""
        
        # 1. 模拟 Question Agent
        mock_gen.return_value = [{"id": 1, "question": "测试题", "answer": "A"}]

        # 2. 模拟 Score Agent 返回低分 (30分，低于 RETRY_THRESHOLD=50)
        mock_grade.return_value = {
            "total_score": 30,
            "weak_points": ["所有内容"],
            "overall_feedback": "需要重修"
        }

        initial_state = {
            "student_id": "low_score_student",
            "skill_title": self.skill_title,
            "skill_content": "",
            "skill_metadata": {},
            "questions": [],
            "student_answers": [],
            "grading_result": {},
            "score_history": [],
            "analysis_report": {},
            "need_retry": False
        }

        # 执行
        final_state = self.app.invoke(initial_state)

        # 验证是否标记了需要复测
        # 注意：在 invoke 中，如果触发了条件边回到 generate_questions，
        # 它会再次执行直到遇到 END 或达到递归上限。
        # 这里我们验证最终产生的 need_retry 状态。
        self.assertEqual(final_state["grading_result"]["total_score"], 30)
        self.assertTrue(final_state["need_retry"])
        print("✅ 复测逻辑测试通过：检测到低分并正确设置了复测标志。")

if __name__ == "__main__":
    unittest.main()

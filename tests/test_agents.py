"""
代理测试
"""

import pytest


class TestAgents:
    """
    代理测试
    """
    
    def setup_method(self):
        """
        设置测试环境
        """
        # 创建测试技能
        self.test_skills = [
            {
                "name": "Paper Review",
                "description": "结构化的学术论文评审框架",
                "content": "# Paper Review\n\n## Process\n1. 阅读论文摘要和引言\n2. 分析研究方法\n3. 评估实验结果\n4. 总结贡献和不足\n5. 提供改进建议"
            },
            {
                "name": "PDF Summary",
                "description": "PDF文档摘要生成工具",
                "content": "# PDF Summary\n\n## Process\n1. 提取PDF文档内容\n2. 识别关键信息\n3. 生成结构化摘要\n4. 突出重点内容"
            }
        ]
    
    def test_skill_management(self):
        """
        测试技能管理功能
        """
        from utils.skill_manager import get_skill_template, create_skill, list_skills
        
        # 测试获取技能模板
        template = get_skill_template()
        assert template is not None
        assert "# {Skill标题}" in template
        
        # 测试创建技能
        test_content = """
        # 测试技能
        
        ## 技能描述
        这是一个测试技能
        
        ## 元数据
        - 技能类型：授课
        - 适用场景：测试场景
        - 难度等级：初级
        - 关键词：测试, 技能
        - 创建者：test_teacher
        - 创建时间：2025-01-26
        
        ## 学习目标
        1. 测试目标1
        2. 测试目标2
        
        ## 内容
        测试技能内容
        """
        # 确保测试技能不存在
        import os
        from utils.skill_manager import SKILL_DIR
        skill_path = os.path.join(SKILL_DIR, "测试技能.md")
        if os.path.exists(skill_path):
            os.remove(skill_path)
        
        result = create_skill("测试技能", test_content, "test_teacher")
        assert result["success"] == True
        
        # 测试列出技能
        skills = list_skills()
        assert len(skills) > 0
        skill_names = [skill.get("标题") for skill in skills]
        assert "测试技能" in skill_names
    
    def test_qa_workflow(self):
        """
        测试QA工作流
        """
        from agents.qa_agent import answer_student_question
        
        # 测试学生提问
        result = answer_student_question("test_student", "什么是互斥？", use_mock=True)
        assert result["success"] == True
        assert "answer" in result
        assert "matched_skills" in result
        assert len(result["matched_skills"]) > 0

"""
代理测试
"""

import pytest
from agents.agentscope.router_agent import SkillRouterAgent
from agents.agentscope.chat_agent import SkillChatAgent


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
    
    def test_skill_router_agent_initialization(self):
        """
        测试技能路由代理初始化
        """
        # 创建代理（使用模拟模型）
        class MockModel:
            def __call__(self, messages):
                class MockResponse:
                    content = '{"use_skills": true, "selected_skills": ["Paper Review"], "rationale": "用户需要论文评审"}'
                return MockResponse()
        
        agent = SkillRouterAgent(
            model=MockModel(),
            skills=self.test_skills,
            max_skills=3
        )
        
        assert agent.skills == self.test_skills
        assert agent.max_skills == 3
    
    def test_skill_chat_agent_initialization(self):
        """
        测试技能聊天代理初始化
        """
        # 创建代理（使用模拟模型）
        class MockModel:
            def __call__(self, messages):
                class MockResponse:
                    content = "这是一个测试响应"
                return MockResponse()
        
        agent = SkillChatAgent(
            model=MockModel(),
            skills=self.test_skills
        )
        
        assert agent.skills == self.test_skills
    
    def test_skill_injection(self):
        """
        测试技能注入
        """
        # 创建代理（使用模拟模型）
        class MockModel:
            def __call__(self, messages):
                class MockResponse:
                    content = "这是一个测试响应"
                return MockResponse()
        
        agent = SkillChatAgent(
            model=MockModel(),
            skills=self.test_skills
        )
        
        # 测试技能注入
        injected_content = agent._inject_skills(["Paper Review"])
        assert "SKILL: Paper Review BEGIN" in injected_content
        assert "阅读论文摘要和引言" in injected_content
        assert "SKILL: Paper Review END" in injected_content

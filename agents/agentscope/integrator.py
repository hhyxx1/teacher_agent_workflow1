"""
AgentScope 集成器
负责整合 Router Agent 和 Chat Agent，提供统一的接口
"""

from typing import Dict, List, Optional
from agentscope.model import ModelWrapper
from agentscope.model import get_model as get_agentscope_model
from .router_agent import SkillRouterAgent
from .chat_agent import SkillChatAgent
from utils.skill_loader import discover_skills


class AgentIntegrator:
    """
    AgentScope 集成器
    """
    
    def __init__(
        self,
        chat_model_name: str = "gpt-3.5-turbo",
        router_model_name: str = "gpt-3.5-turbo",
        skills_dir: str = "skills",
        max_skills: int = 3,
    ):
        """
        初始化集成器
        
        Args:
            chat_model_name: 聊天模型名称
            router_model_name: 路由模型名称
            skills_dir: 技能目录
            max_skills: 最大技能数量
        """
        # 加载技能
        self.skills = discover_skills(skills_dir)
        self.skills_dir = skills_dir
        self.max_skills = max_skills
        
        # 初始化模型
        self.chat_model = get_agentscope_model(
            model_type="openai",
            model_name=chat_model_name,
        )
        
        self.router_model = get_agentscope_model(
            model_type="openai",
            model_name=router_model_name,
        )
        
        # 初始化代理
        self.router_agent = SkillRouterAgent(
            model=self.router_model,
            skills=self.skills,
            max_skills=max_skills,
        )
        
        self.chat_agent = SkillChatAgent(
            model=self.chat_model,
            skills=self.skills,
        )
    
    def reload_skills(self):
        """
        重新加载技能
        """
        self.skills = discover_skills(self.skills_dir)
        self.router_agent.skills = self.skills
        self.chat_agent.skills = self.skills
    
    def process_query(self, user_query: str) -> Dict:
        """
        处理用户查询
        
        Args:
            user_query: 用户查询内容
            
        Returns:
            Dict: 包含响应、使用的技能和决策理由的字典
        """
        # 路由决策
        routing_decision = self.router_agent.route(user_query)
        
        # 生成响应
        response = self.chat_agent.generate_response(
            user_query=user_query,
            selected_skills=routing_decision.selected_skills if routing_decision.use_skills else []
        )
        
        return {
            "response": response,
            "use_skills": routing_decision.use_skills,
            "selected_skills": routing_decision.selected_skills,
            "rationale": routing_decision.rationale
        }
    
    def run_workflow(self, student_id: str, skill_title: str) -> Dict:
        """
        运行工作流
        
        Args:
            student_id: 学生ID
            skill_title: 技能标题
            
        Returns:
            Dict: 工作流执行结果
        """
        return self.chat_agent.run_workflow(student_id, skill_title)
    
    def get_available_skills(self) -> List[Dict]:
        """
        获取可用的技能列表
        
        Returns:
            List[Dict]: 技能列表
        """
        return self.skills
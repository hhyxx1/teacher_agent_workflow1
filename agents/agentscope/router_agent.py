"""
技能路由代理
负责分析用户查询并选择合适的技能
"""

import json
from typing import List, Dict, Optional
from pydantic import BaseModel, Field
from agentscope.agent import AgentBase
from agentscope.message import Msg
from utils.logger import logger, log_function_call


class SkillRoutingDecision(BaseModel):
    """技能路由决策模型"""
    use_skills: bool = Field(..., description="是否使用技能")
    selected_skills: List[str] = Field(default_factory=list, description="选中的技能列表")
    rationale: str = Field(..., description="决策理由")


class SkillRouterAgent(AgentBase):
    """技能路由代理"""
    
    def __init__(
        self,
        name: str = "SkillRouter",
        model = None,
        skills: List[Dict] = None,
        max_skills: int = 3,
    ):
        super().__init__()
        self.name = name
        self.model = model
        self.skills = skills or []
        self.max_skills = max_skills
        self.system_prompt = self._build_system_prompt()
    
    def _build_system_prompt(self) -> str:
        """构建系统提示"""
        skill_descriptions = []
        for skill in self.skills:
            skill_descriptions.append(f"- {skill['name']}: {skill.get('description', '无描述')}")
        
        return f"""
你是一个智能技能路由器，负责分析用户查询并选择最合适的技能。

可用技能：
{chr(10).join(skill_descriptions)}

请根据用户的查询，决定是否使用技能以及使用哪些技能。

决策规则：
1. 只有当用户查询与某个技能的用途明确相关时，才选择该技能
2. 最多选择 {self.max_skills} 个技能
3. 确保选择的技能名称与可用技能列表中的名称完全匹配
4. 提供清晰的决策理由

请以严格的JSON格式返回决策结果：
{{
  "use_skills": true/false,
  "selected_skills": ["技能1", "技能2"],
  "rationale": "决策理由"
}}
        """
    
    @log_function_call
    def route(self, user_query: str) -> SkillRoutingDecision:
        """
        分析用户查询并返回技能路由决策
        
        Args:
            user_query: 用户查询内容
            
        Returns:
            SkillRoutingDecision: 技能路由决策
        """
        logger.info(f"分析用户查询: {user_query[:50]}...")
        
        # 构建消息
        messages = [
            Msg(role="system", content=self.system_prompt),
            Msg(role="user", content=user_query)
        ]
        
        # 发送消息并获取响应
        response = self.model(messages)
        
        # 解析响应
        for i in range(3):  # 最多重试3次
            try:
                decision_data = json.loads(response.content)
                decision = SkillRoutingDecision(**decision_data)
                
                # 验证技能名称
                valid_skills = [skill['name'] for skill in self.skills]
                invalid_skills = [s for s in decision.selected_skills if s not in valid_skills]
                
                if invalid_skills:
                    logger.warning(f"无效的技能名称: {invalid_skills}")
                    decision.selected_skills = [s for s in decision.selected_skills if s in valid_skills]
                
                # 限制技能数量
                if len(decision.selected_skills) > self.max_skills:
                    logger.info(f"技能数量超过限制，截断到 {self.max_skills} 个")
                    decision.selected_skills = decision.selected_skills[:self.max_skills]
                
                logger.info(f"路由决策: 使用技能={decision.use_skills}, 选择的技能={decision.selected_skills}")
                return decision
                
            except json.JSONDecodeError:
                logger.warning(f"JSON解析失败，第{i+1}次重试...")
                # 重试
                retry_prompt = "请以严格的JSON格式返回决策结果，不要包含任何额外内容。"
                messages.append(Msg(role="assistant", content=response.content))
                messages.append(Msg(role="user", content=retry_prompt))
                response = self.model(messages)
            except Exception as e:
                logger.error(f"解析响应失败: {e}")
                break
        
        # 降级处理：不使用技能
        logger.warning("无法解析决策结果，降级为不使用技能")
        return SkillRoutingDecision(
            use_skills=False,
            selected_skills=[],
            rationale="无法解析决策结果，降级为不使用技能"
        )
import os
import sys
import json
from typing import List, Optional, Dict

# 添加根目录到路径以便导入现有的 utils 和 config
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))

from backend.app.utils.skill_manager import load_skill
from backend.app.config import get_llm

class SkillService:
    def __init__(self, skills_dir: str = "skills"):
        self.skills_dir = skills_dir
        self.llm = get_llm()

    def list_available_skills(self) -> List[Dict]:
        """列出所有可用的 Skill 及其元数据"""
        skills_metadata = []
        if not os.path.exists(self.skills_dir):
            return []
        
        for filename in os.listdir(self.skills_dir):
            if filename.endswith(".md"):
                skill_id = filename[:-3]
                skill_data = load_skill(skill_id)
                if skill_data:
                    skills_metadata.append({
                        "id": skill_id,
                        "name": skill_data.get("name", skill_id),
                        "description": skill_data.get("description", ""),
                        "tags": skill_data.get("tags", [])
                    })
        return skills_metadata

    def find_best_match(self, query: str) -> Optional[str]:
        """使用 LLM 根据用户问题匹配最合适的 Skill ID"""
        skills = self.list_available_skills()
        if not skills:
            return None

        # 构建匹配 Prompt
        skills_str = "\n".join([f"- ID: {s['id']}, Name: {s['name']}, Description: {s['description']}" for s in skills])
        
        prompt = f"""
你是一个专业的教学助手。请根据学生的提问，从以下可选的教学技能(Skill)列表中选择一个最相关的。

学生提问: "{query}"

可选技能列表:
{skills_str}

请仅返回匹配的 Skill ID。如果没有合适的匹配，请返回 "None"。
注意：只返回 ID 字符串，不要有任何其他解释。
"""
        response = self.llm.invoke(prompt)
        match_id = response.content.strip().strip('"').strip("'")
        
        if match_id == "None" or not any(s['id'] == match_id for s in skills):
            return None
            
        return match_id

    def get_skill_content(self, skill_id: str) -> Optional[str]:
        """获取指定 Skill 的详细内容"""
        skill_data = load_skill(skill_id)
        return skill_data.get("content") if skill_data else None

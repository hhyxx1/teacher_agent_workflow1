"""
AgentScope 配置模块
负责管理 AgentScope 相关的配置选项
从 config.py 导入共享配置，避免重复配置
"""

from typing import Optional
from config import (
    API_KEY as OPENAI_API_KEY,
    BASE_URL as OPENAI_BASE_URL,
    DEFAULT_CHAT_MODEL,
    DEFAULT_ROUTER_MODEL,
    SKILL_DIR as DEFAULT_SKILLS_DIR,
    MAX_SKILLS_PER_QUERY,
    MAX_SESSION_MEMORY,
    LOG_LEVEL,
    validate_config as validate_base_config,
    get_agentscope_model_config
)

# =================================================================
# 验证配置
# =================================================================
def validate_config() -> tuple[bool, Optional[str]]:
    """
    验证配置
    
    Returns:
        tuple[bool, Optional[str]]: (是否有效, 错误信息)
    """
    return validate_base_config()
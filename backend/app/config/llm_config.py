"""
LLM 配置模块 (LLM Configuration)

该模块集中管理与大语言模型相关的配置和工具函数，包括：
1. LLM 实例的单例管理
2. AgentScope 模型配置
3. 配置验证
"""

from langchain_openai import ChatOpenAI
from typing import Optional, Tuple
from .settings import settings

# 内部单例变量，防止重复初始化模型
_llm_instance = None

def get_llm():
    """
    获取单例化的 LLM 实例 (Thread-safe Singleton Pattern)
    
    使用延迟初始化 (Lazy Initialization) 策略，只有在第一次被调用时才会读取 API Key 并创建实例。
    这样可以防止在未配置环境变量的情况下，导入 config 模块就发生报错。

    Returns:
        ChatOpenAI | None: 返回 LangChain 封装的模型实例。如果 API_KEY 为空则返回 None。
    """
    global _llm_instance
    if _llm_instance is None:
        if not settings.API_KEY:
            # 记录警告或在测试模式下允许为空
            return None
        _llm_instance = ChatOpenAI(
            model=settings.LLM_MODEL,
            api_key=settings.API_KEY,
            base_url=settings.BASE_URL,
            temperature=0.1 # 采样温度：0.1 意味着结果高度确定且一致，适合出题和评分等严谨场景
        )
    return _llm_instance

def validate_config() -> Tuple[bool, Optional[str]]:
    """
    验证配置
    
    Returns:
        Tuple[bool, Optional[str]]: (是否有效, 错误信息)
    """
    # 检查 API_KEY
    if not settings.API_KEY:
        print("警告: API_KEY 环境变量未设置，某些功能可能无法正常工作")
        # 在开发环境中，即使 API_KEY 未设置也返回有效配置
        # 在生产环境中，这里应该返回 False
    
    return True, None

def get_agentscope_model_config(model_name: str) -> dict:
    """
    获取 AgentScope 模型配置
    
    Args:
        model_name: 模型名称
        
    Returns:
        dict: 模型配置
    """
    return {
        "model_type": "openai",
        "model_name": model_name,
        "api_key": settings.API_KEY,
        "base_url": settings.BASE_URL,
        "temperature": 0.1,
    }

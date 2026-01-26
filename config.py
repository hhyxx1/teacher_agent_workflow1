"""
全局配置模块 (Global Configuration)

该模块集中管理项目的所有配置项，包括：
1. LLM (大语言模型) 参数：支持 OpenAI 兼容接口，默认适配 DeepSeek。
2. 路径配置：定义数据存储、技能描述文件等目录结构。
3. 业务阈值：定义及格线、复测逻辑等核心教学参数。
4. AgentScope 配置：用于多模型支持和代理管理。

使用方式：
    从本模块直接导入常量，或通过 get_llm() 获取单例化的模型实例。
"""

import os
from langchain_openai import ChatOpenAI
from typing import Optional, Tuple

# =================================================================
# 1. LLM 配置 (Large Language Model Configuration)
# =================================================================
# 模型标识符：默认为 deepseek-chat，可根据需求修改为 gpt-4o 等
LLM_MODEL = os.getenv("LLM_MODEL", "deepseek-chat")

# API 密钥：必须在环境变量中配置 API_KEY 以确保安全
# Windows 设置命令: $env:API_KEY="your_key_here"
# Linux/Mac 设置命令: export API_KEY="your_key_here"
API_KEY = os.getenv("API_KEY")

# API 基础地址：DeepSeek 默认为 https://api.deepseek.com
BASE_URL = os.getenv("BASE_URL", "https://api.deepseek.com")

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
        if not API_KEY:
            # 记录警告或在测试模式下允许为空
            return None
        _llm_instance = ChatOpenAI(
            model=LLM_MODEL,
            api_key=API_KEY,
            base_url=BASE_URL,
            temperature=0.1 # 采样温度：0.1 意味着结果高度确定且一致，适合出题和评分等严谨场景
        )
    return _llm_instance

# =================================================================
# 2. 路径配置 (FileSystem Paths)
# =================================================================
# 所有路径均相对于项目根目录
SKILL_DIR = "skills"                    # 存放 Skill Markdown (教师编写的教学大纲)
DATA_DIR = "data"                      # 数据根目录
QUESTION_DIR = f"{DATA_DIR}/questions" # 存储每日为学生个性化生成的题目 (JSON)
SCORE_DIR = f"{DATA_DIR}/scores"       # 存储学生的历史得分记录 (JSONL, 追加写入)
LOG_DIR = "logs"                       # 日志目录

# =================================================================
# 3. 教学业务参数 (Education Business Parameters)
# =================================================================
NUM_QUESTIONS_PER_DAY = 5    # 每日建议测试题量：控制 LLM 生成的 JSON 数组长度
PASS_SCORE = 60              # 及格分数线：用于进度分析的基准
RETRY_THRESHOLD = 50         # 强制复测阈值：若今日总分低于此值，工作流将自动重定向回出题节点

# =================================================================
# 4. AgentScope 配置
# =================================================================
# 模型配置
DEFAULT_CHAT_MODEL = os.getenv("CHAT_MODEL", "gpt-3.5-turbo")
DEFAULT_ROUTER_MODEL = os.getenv("ROUTER_MODEL", "gpt-3.5-turbo")

# 技能配置
MAX_SKILLS_PER_QUERY = int(os.getenv("MAX_SKILLS", "3"))

# 会话配置
MAX_SESSION_MEMORY = int(os.getenv("MAX_SESSION_MEMORY", "10"))

# 日志配置
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# =================================================================
# 5. 配置验证
# =================================================================
def validate_config() -> Tuple[bool, Optional[str]]:
    """
    验证配置
    
    Returns:
        Tuple[bool, Optional[str]]: (是否有效, 错误信息)
    """
    # 检查 API_KEY
    if not API_KEY:
        return False, "API_KEY 环境变量未设置"
    
    # 检查必要的目录
    for directory in [SKILL_DIR, DATA_DIR, QUESTION_DIR, SCORE_DIR, LOG_DIR]:
        if not os.path.exists(directory):
            try:
                os.makedirs(directory, exist_ok=True)
            except Exception as e:
                return False, f"无法创建目录 {directory}: {e}"
    
    return True, None

# =================================================================
# 6. AgentScope 模型配置
# =================================================================
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
        "api_key": API_KEY,
        "base_url": BASE_URL,
        "temperature": 0.1,
    }


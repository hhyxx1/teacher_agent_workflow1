import os
from langchain_openai import ChatOpenAI

# LLM 配置
# 支持 DeepSeek API（兼容 OpenAI 格式）
LLM_MODEL = os.getenv("LLM_MODEL", "deepseek-chat")  # 默认使用 deepseek-chat
API_KEY = os.getenv("API_KEY")  # 通用 API Key 环境变量
BASE_URL = os.getenv("BASE_URL", "https://api.deepseek.com")  # DeepSeek API 地址

# 延迟初始化LLM（仅在需要时初始化）
_llm_instance = None

def get_llm():
    """获取LLM实例（延迟初始化）"""
    global _llm_instance
    if _llm_instance is None:
        if not API_KEY:
            # 如果没有API_KEY，返回None（用于测试模式）
            return None
        _llm_instance = ChatOpenAI(
            model=LLM_MODEL,
            api_key=API_KEY,
            base_url=BASE_URL,
            temperature=0.1
        )
    return _llm_instance

# 向后兼容的llm变量（延迟初始化）
llm = None

# 路径
SKILL_DIR = "skills"
DATA_DIR = "data"
QUESTION_DIR = f"{DATA_DIR}/questions"
SCORE_DIR = f"{DATA_DIR}/scores"

# 出题/评分参数
NUM_QUESTIONS_PER_DAY = 5
PASS_SCORE = 60
RETRY_THRESHOLD = 50  # <50分需要复测


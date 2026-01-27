import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # 应用配置
    APP_NAME: str = "智能教学平台"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # 服务器配置
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # PostgreSQL数据库配置
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/education_db"
    # 异步数据库URL（用于asyncpg）
    ASYNC_DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost:5432/education_db"
    
    # 向量数据库配置（知识库）
    VECTOR_DB_PATH: str = "./data/chroma_db"
    PGVECTOR_ENABLED: bool = False  # 是否使用pgvector扩展
    
    # 安全配置
    SECRET_KEY: str = "your-secret-key-here-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS配置
    CORS_ORIGINS: list = ["http://localhost:3000"]
    
    # LLM 配置
    LLM_MODEL: str = "deepseek-chat"
    API_KEY: str = ""
    BASE_URL: str = "https://api.deepseek.com"
    
    # 教学业务参数
    NUM_QUESTIONS_PER_DAY: int = 5
    PASS_SCORE: int = 60
    RETRY_THRESHOLD: int = 50
    
    # AgentScope 配置
    DEFAULT_CHAT_MODEL: str = "gpt-3.5-turbo"
    DEFAULT_ROUTER_MODEL: str = "gpt-3.5-turbo"
    MAX_SKILLS_PER_QUERY: int = 3
    MAX_SESSION_MEMORY: int = 10
    
    class Config:
        env_file = ".env"

settings = Settings()

# 路径配置
BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILL_DIR = os.path.join(BASE_PATH, "skills")
DATA_DIR = os.path.join(BASE_PATH, "data")
QUESTION_DIR = os.path.join(DATA_DIR, "questions")
SCORE_DIR = os.path.join(DATA_DIR, "scores")

# 确保目录存在
for directory in [SKILL_DIR, DATA_DIR, QUESTION_DIR, SCORE_DIR]:
    os.makedirs(directory, exist_ok=True)

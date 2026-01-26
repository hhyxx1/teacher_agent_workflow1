import os
from langchain_openai import ChatOpenAI

# LLM 配置
LLM_MODEL = "gpt-3.5-turbo"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
llm = ChatOpenAI(model=LLM_MODEL, api_key=OPENAI_API_KEY, temperature=0.1)

# 路径
SKILL_DIR = "skills"
DATA_DIR = "data"
QUESTION_DIR = f"{DATA_DIR}/questions"
SCORE_DIR = f"{DATA_DIR}/scores"

# 出题/评分参数
NUM_QUESTIONS_PER_DAY = 5
PASS_SCORE = 60
RETRY_THRESHOLD = 50  # <50分需要复测


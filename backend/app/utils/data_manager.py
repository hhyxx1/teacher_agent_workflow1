"""
数据管理模块 (Data Manager)

职责：
    负责所有本地文件的数据持久化操作，包括题目 (JSON) 和成绩 (JSONL) 的读写。
    封装了文件路径生成、目录自动创建等底层逻辑，向上层提供简洁的接口。

目录规范：
    - data/questions/: 存储每日生成的题目文件
    - data/scores/: 存储学生的历史成绩记录
"""

import os
import json
from datetime import date
from app.config.settings import QUESTION_DIR, SCORE_DIR

# 确保目录存在
os.makedirs(QUESTION_DIR, exist_ok=True)
os.makedirs(SCORE_DIR, exist_ok=True)

def save_daily_questions(student_id: str, questions: list[dict]):
    """
    保存每日生成的题目到本地 JSON 文件
    
    文件名格式: {student_id}_{yyyy-mm-dd}.json
    例如: student_001_2023-10-27.json
    
    Args:
        student_id (str): 学生唯一标识
        questions (list[dict]): 包含题目信息的字典列表
    """
    today = date.today().isoformat()
    path = f"{QUESTION_DIR}/{student_id}_{today}.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(questions, f, ensure_ascii=False, indent=2)

def load_daily_questions(student_id: str) -> list[dict]:
    """
    尝试加载今日已生成的题目
    
    用于缓存机制，避免同一天内重复调用 LLM 生成题目。
    
    Returns:
        list[dict]: 题目列表。如果文件不存在，返回 None。
    """
    today = date.today().isoformat()
    path = f"{QUESTION_DIR}/{student_id}_{today}.json"
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return None

def save_score(score_record: dict):
    """
    保存单次评分结果 (Append Mode)
    
    使用 JSON Lines (JSONL) 格式存储，每个学生的成绩存放在单独的文件中。
    文件名格式: {student_id}_scores.jsonl
    
    Args:
        score_record (dict): 包含 student_id, skill, score, weak_points 等字段的字典
    """
    path = f"{SCORE_DIR}/{score_record['student_id']}_scores.jsonl"
    # 添加时间戳
    score_record["date"] = date.today().isoformat()
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(score_record, ensure_ascii=False) + "\n")

def load_score_history(student_id: str) -> list[dict]:
    """
    加载指定学生的所有历史成绩
    
    Args:
        student_id (str): 学生唯一标识
        
    Returns:
        list[dict]: 按时间顺序排列的成绩记录列表。如果无记录，返回空列表。
    """
    path = f"{SCORE_DIR}/{student_id}_scores.jsonl"
    history = []
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    history.append(json.loads(line))
    return history

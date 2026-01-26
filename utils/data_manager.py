import os
import json
from datetime import date
from config import QUESTION_DIR, SCORE_DIR

os.makedirs(QUESTION_DIR, exist_ok=True)
os.makedirs(SCORE_DIR, exist_ok=True)

def save_daily_questions(student_id: str, questions: list[dict]):
    today = date.today().isoformat()
    path = f"{QUESTION_DIR}/{student_id}_{today}.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(questions, f, ensure_ascii=False, indent=2)

def load_daily_questions(student_id: str) -> list[dict]:
    today = date.today().isoformat()
    path = f"{QUESTION_DIR}/{student_id}_{today}.json"
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_score(student_id: str, score_result: dict, skill_title: str):
    today = date.today().isoformat()
    record = {
        "date": today,
        "skill": skill_title,
        **score_result
    }
    path = f"{SCORE_DIR}/{student_id}.jsonl"
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")

def load_score_history(student_id: str) -> list[dict]:
    path = f"{SCORE_DIR}/{student_id}.jsonl"
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


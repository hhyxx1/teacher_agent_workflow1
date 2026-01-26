def analyze_progress(score_history: list[dict], skill_title: str) -> dict:
    """按Skill分析进步：趋势、提升幅度、薄弱点"""
    records = [r for r in score_history if r.get("skill") == skill_title]
    if len(records) < 2:
        return {"status": "insufficient_data", "message": "至少需要2次测试"}

    scores = [r["total_score"] for r in records]
    first = scores[0]
    latest = scores[-1]
    improvement = latest - first
    trend = "up" if improvement > 0 else "down" if improvement < 0 else "flat"

    return {
        "skill": skill_title,
        "test_count": len(records),
        "first_score": first,
        "latest_score": latest,
        "improvement": improvement,
        "trend": trend,
        "suggestion": _get_suggestion(trend, improvement, latest)
    }

def _get_suggestion(trend, improvement, latest):
    if trend == "up":
        if improvement >= 20:
            return "进步显著，继续保持，可挑战更高难度题目"
        elif improvement >= 10:
            return "稳步提升，建议加强错题复习"
        else:
            return "小幅进步，需多练习基础题"
    elif trend == "down":
        return "分数下滑，建议回顾Skill核心知识点，重做错题"
    else:
        return "分数平稳，可尝试拓展同Skill的进阶题目"


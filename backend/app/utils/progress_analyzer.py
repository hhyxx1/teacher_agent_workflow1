"""
进步分析器
负责根据学生的历史成绩记录，分析学习趋势并给出建议。
"""

def analyze_progress(score_history: list[dict], skill_title: str) -> dict:
    """
    按 Skill 分析学生的进步情况
    
    Args:
        score_history (list[dict]): 学生的完整历史成绩单
        skill_title (str): 需要分析的特定 Skill 标题
        
    Returns:
        dict: 包含趋势、改进分、趋势类型和建议的分析报告
    """
    # 筛选出当前 Skill 的历史记录
    records = [r for r in score_history if r.get("skill") == skill_title]
    
    # 至少需要两次记录才能分析趋势
    if len(records) < 2:
        return {"status": "insufficient_data", "message": "至少需要2次测试才能分析进步趋势"}

    # 提取总分序列
    scores = [r["score"] for r in records]
    first = scores[0]
    latest = scores[-1]
    
    # 计算分差
    improvement = latest - first
    
    # 判断趋势方向
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

def _get_suggestion(trend: str, improvement: int, latest: int) -> str:
    """
    根据趋势和分数生成具体建议（内部辅助函数）
    """
    if trend == "up":
        if improvement >= 20:
            return "进步显著，继续保持，可挑战更高难度题目"
        elif improvement >= 10:
            return "稳步提升，建议加强错题复习，巩固成果"
        else:
            return "小幅进步，需多练习基础题，打牢基础"
    elif trend == "down":
        return "分数下滑，建议回顾 Skill 核心知识点，重做错题"
    else:
        return "分数平稳，可尝试拓展同 Skill 的进阶题目"


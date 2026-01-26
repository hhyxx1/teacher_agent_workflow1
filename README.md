# Teacher Agent Workflow

本项目是一个基于 LangGraph 的教师 AI 工作流，旨在自动化出题、评分和学生进度分析。

## 文件架构
- `main.py`: 入口：启动 LangGraph 工作流
- `config.py`: 配置：LLM、路径、阈值
- `skills/`: 教师 Skill（MD）
- `data/`: 学生数据（题目、分数）
- `agents/`: Agent 模块（出题、评分）
- `graph/`: LangGraph 工作流定义
- `utils/`: 工具类（加载、管理、分析）

## 运行说明
1. 配置 `config.py` 中的 LLM 参数。
2. 运行 `python main.py` 启动工作流。

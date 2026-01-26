# Skill创建、共享与应用 - 功能设计文档

## 1. 工作流设计

### 1.1 Skill创建工作流
```
教师 → 创建Skill(MD格式) → 元数据验证 → 保存到系统 → 索引更新
```

**核心功能**：
- Skill模板生成
- 元数据标准化验证
- Skill保存与索引

### 1.2 学生提问-匹配-回答工作流
```
学生提问 → 语义搜索匹配Skill → 提取相关内容 → LLM生成回答 → 返回结果
```

**核心功能**：
- 学生提问接口
- Skill语义匹配（向量搜索）
- 基于Skill上下文生成回答

### 1.3 Skill共享工作流
```
教师A → 浏览Skill库 → 选择Skill → Fork/复用 → 修改定制 → 保存为新Skill
```

**核心功能**：
- Skill列表/搜索
- Skill复用机制
- 权限管理

---

## 2. Skill MD格式规范

```markdown
# {Skill标题}

## 技能描述
{一句话描述skill用途}

## 元数据
- 技能类型：面试/授课/代码分析/其他
- 适用场景：{使用场景描述}
- 难度等级：初级/中级/高级
- 关键词：keyword1, keyword2, keyword3
- 创建者：{教师ID}
- 创建时间：{YYYY-MM-DD}

## 学习目标
1. 目标1
2. 目标2
3. 目标3

## 内容
{详细教学内容}

### 核心概念
{概念解释}

### 案例分析
{实际案例}

### 常见问题
{FAQ}

## 参考资料
- 资料1
- 资料2
```

---

## 3. 技术实现方案

### 3.1 Skill管理模块
**文件**: `utils/skill_manager.py`

功能：
- `create_skill()`: 创建新skill
- `list_skills()`: 列出所有skill
- `search_skills()`: 搜索skill
- `fork_skill()`: 复用skill
- `validate_skill()`: 验证skill格式

### 3.2 Skill匹配模块
**文件**: `agents/qa_agent.py`

功能：
- `match_skill_for_question()`: 根据问题匹配skill
- `generate_answer_with_skill()`: 基于skill生成回答

技术选型：
- **简单版本**: 关键词匹配
- **进阶版本**: 向量embedding + 语义搜索

### 3.3 QA工作流
**文件**: `graph/qa_workflow.py`

节点：
1. 接收学生提问
2. 搜索匹配skill
3. 提取skill相关内容
4. LLM生成回答
5. 返回结果

---

## 4. 数据存储结构

```
data/
├── skills/              # Skill MD文件
│   ├── skill1.md
│   └── skill2.md
├── skill_index.json     # Skill索引（元数据+关键词）
├── questions/           # 学生题目（现有）
└── scores/             # 学生成绩（现有）
```

---

## 5. API接口设计（供前端调用）

### 5.1 Skill创建
```python
POST /api/skills/create
{
  "title": "skill标题",
  "content": "MD内容",
  "metadata": {...}
}
```

### 5.2 学生提问
```python
POST /api/qa/ask
{
  "student_id": "student_001",
  "question": "什么是进程同步？"
}
Response: {
  "answer": "...",
  "matched_skill": "同步与互斥教学案例",
  "references": [...]
}
```

### 5.3 Skill搜索
```python
GET /api/skills/search?keyword=同步&type=授课
Response: [{
  "title": "...",
  "description": "...",
  "metadata": {...}
}]
```

---

## 6. 实现优先级

### Phase 1: 核心功能（本次实现）
- [x] Skill标准格式定义
- [ ] Skill管理模块
- [ ] 学生提问-匹配-回答工作流（简单版：关键词匹配）
- [ ] Skill索引系统

### Phase 2: 增强功能
- [ ] 语义搜索（向量embedding）
- [ ] Skill版本管理
- [ ] 权限管理

### Phase 3: 优化
- [ ] 推荐算法
- [ ] 学习路径规划

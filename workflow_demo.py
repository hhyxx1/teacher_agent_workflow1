"""
演示脚本：Skill创建、共享、应用工作流完整测试
"""
import sys
from utils.skill_manager import (
    get_skill_template,
    create_skill,
    list_skills,
    search_skills,
    fork_skill,
    get_skill_detail,
    rebuild_skill_index
)
from agents.qa_agent import answer_student_question


def demo_skill_management():
    """演示Skill管理功能"""
    print("\n" + "="*70)
    print("【演示 1】Skill 管理功能")
    print("="*70)

    # 1.1 创建新Skill
    print("\n[1.1] 创建新Skill：链表数据结构")
    print("-" * 70)

    new_skill_content = """# 链表数据结构

## 技能描述
通过讲解链表的基本概念、常见操作和应用，帮助学生掌握链表这一重要的数据结构

## 元数据
- 技能类型：授课
- 适用场景：数据结构课程、算法教学、面试准备
- 难度等级：初级
- 关键词：链表, 指针, 数据结构, 内存管理, 递归
- 创建者：teacher_002
- 创建时间：2025-01-26

## 学习目标
1. 理解链表的基本结构和特点
2. 掌握链表的基本操作（插入、删除、查询）
3. 理解链表与数组的差异及应用场景
4. 能够解决简单的链表问题

## 内容

### 链表的定义
链表是由节点组成的线性数据结构，每个节点包含数据和指向下一个节点的指针。

### 基本操作
- 查询：O(n)
- 插入：O(1)（已知位置）
- 删除：O(1)（已知位置）

### 常见问题
- 反转链表
- 检测环
- 合并链表

## 参考资料
- Introduction to Algorithms
- LeetCode链表专题
"""

    result = create_skill("链表数据结构", new_skill_content, "teacher_002")
    if result["success"]:
        print(f"✓ Skill创建成功：{result['skill_title']}")
        if result.get("warnings"):
            print(f"  警告：{result['warnings']}")
    else:
        print(f"✗ Skill创建失败：{result['errors']}")

    # 1.2 列出所有Skill
    print("\n[1.2] 列出系统中的所有Skill")
    print("-" * 70)
    skills = list_skills()
    print(f"找到 {len(skills)} 个Skill：")
    for i, skill in enumerate(skills, 1):
        print(f"  {i}. {skill.get('标题')} [{skill.get('技能类型', 'N/A')}] - {skill.get('技能描述', '')[:50]}")

    # 1.3 按类型筛选
    print("\n[1.3] 按类型筛选Skill（类型=授课）")
    print("-" * 70)
    teaching_skills = list_skills(skill_type="授课")
    print(f"找到 {len(teaching_skills)} 个授课类型的Skill：")
    for skill in teaching_skills:
        print(f"  • {skill.get('标题')}")

    # 1.4 搜索Skill
    print("\n[1.4] 搜索Skill（关键词=信号量）")
    print("-" * 70)
    matched = search_skills("信号量")
    if matched:
        print(f"搜索结果（共 {len(matched)} 项）：")
        for skill in matched:
            print(f"  • {skill.get('标题')} (匹配分数: {skill.get('_match_score', 0)})")
            print(f"    描述：{skill.get('技能描述', 'N/A')[:60]}")
    else:
        print("  未找到相关Skill")

    # 1.5 Fork Skill
    print("\n[1.5] Fork现有Skill（复用创建教学案例）")
    print("-" * 70)
    fork_result = fork_skill(
        "同步与互斥教学案例",
        "同步与互斥教学案例-定制版",
        "teacher_003",
        modifications="• 增加了死锁检测算法的讲解\n• 补充了实际编程示例"
    )
    if fork_result["success"]:
        print(f"✓ Fork成功：{fork_result['skill_title']}")
    else:
        print(f"✗ Fork失败：{fork_result['errors']}")

    # 1.6 查看Skill详情
    print("\n[1.6] 查看Skill完整信息")
    print("-" * 70)
    detail = get_skill_detail("同步与互斥教学案例")
    if detail:
        print(f"标题：{detail['title']}")
        print(f"元数据：")
        for key, value in detail['metadata'].items():
            print(f"  • {key}: {value}")
        print(f"内容预览：{detail['content'][:150]}...")
    else:
        print("  Skill不存在")


def demo_qa_workflow():
    """演示学生提问-匹配-回答工作流"""
    print("\n" + "="*70)
    print("【演示 2】学生提问 → 匹配Skill → 生成回答")
    print("="*70)

    questions = [
        "什么是互斥和同步？有什么区别？",
        "生产者-消费者问题怎么解决？",
        "链表插入操作的时间复杂度是多少？",
        "什么是死锁？",
    ]

    for idx, question in enumerate(questions, 1):
        print(f"\n[问题 {idx}] {question}")
        print("-" * 70)

        # 调用QA工作流（使用模拟模式，不需要API Key）
        result = answer_student_question("student_001", question, use_mock=True)

        if result["success"]:
            print(f"✓ 回答成功")
            print(f"\n参考Skill（共 {result['reference_count']} 个）:")
            for skill in result["matched_skills"]:
                print(f"  • {skill['title']} [{skill['type']}] (匹配分数: {skill['score']})")
            print(f"\n回答内容（前500字）:")
            answer_preview = result["answer"][:500]
            print(answer_preview + "..." if len(result["answer"]) > 500 else answer_preview)
        else:
            print(f"✗ 回答失败：{result['error']}")


def show_skill_management_api():
    """展示Skill管理API文档"""
    print("\n" + "="*70)
    print("【API 文档】Skill管理和QA接口")
    print("="*70)

    api_doc = """
### 1. Skill管理接口

#### 1.1 获取Skill模板
```python
from utils.skill_manager import get_skill_template
template = get_skill_template()
```

#### 1.2 创建Skill
```python
from utils.skill_manager import create_skill
result = create_skill(
    title="技能标题",
    content="MD格式内容",
    teacher_id="teacher_001"
)
```

#### 1.3 列出Skill
```python
from utils.skill_manager import list_skills
skills = list_skills(
    skill_type="授课",  # 可选：按类型筛选
    keywords=["同步", "互斥"]  # 可选：按关键词筛选
)
```

#### 1.4 搜索Skill
```python
from utils.skill_manager import search_skills
matched = search_skills("关键词")
# 返回按匹配分数排序的Skill列表
```

#### 1.5 Fork Skill
```python
from utils.skill_manager import fork_skill
result = fork_skill(
    original_title="原Skill标题",
    new_title="新Skill标题",
    teacher_id="teacher_002",
    modifications="修改说明"  # 可选
)
```

#### 1.6 获取Skill详情
```python
from utils.skill_manager import get_skill_detail
detail = get_skill_detail("技能标题")
# 返回: {title, metadata, content, file_path}
```

### 2. 学生QA接口

#### 2.1 学生提问
```python
from agents.qa_agent import answer_student_question
result = answer_student_question(
    student_id="student_001",
    question="你的问题"
)
# 返回: {success, answer, matched_skills, reference_count}
```

#### 2.2 匹配Skill
```python
from agents.qa_agent import match_skill_for_question
matched = match_skill_for_question(
    question="你的问题",
    top_k=3  # 返回前3个匹配
)
```

#### 2.3 生成回答
```python
from agents.qa_agent import generate_answer_with_skill
result = generate_answer_with_skill(
    question="你的问题",
    matched_skills=[...]  # 匹配的Skill列表
)
```

### 3. 索引管理

#### 重建Skill索引
```python
from utils.skill_manager import rebuild_skill_index
rebuild_skill_index()
# 扫描skills目录，更新索引
```
"""

    print(api_doc)


def main():
    """主函数"""
    print("\n" + "🚀 " * 30)
    print("Skill创建、共享、应用 - 完整工作流演示")
    print("🚀 " * 30)

    # 重建索引（扫描已有的Skill）
    print("\n[初始化] 扫描现有Skill并建立索引...")
    rebuild_skill_index()

    # 运行演示
    try:
        demo_skill_management()
        demo_qa_workflow()
        show_skill_management_api()
    except Exception as e:
        print(f"\n✗ 演示过程中出错：{e}")
        import traceback
        traceback.print_exc()

    print("\n" + "="*70)
    print("演示完成！")
    print("="*70)
    print("\n💡 后续步骤：")
    print("  1. 将这些API集成到Flask/FastAPI后端服务")
    print("  2. 为前端提供RESTful接口")
    print("  3. 集成向量数据库实现语义搜索")
    print("  4. 添加学生学习记录和个性化推荐")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()

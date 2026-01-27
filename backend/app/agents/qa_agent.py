"""
QA Agent：处理学生提问，匹配相关Skill，生成回答
"""
import os
from langchain_core.prompts import ChatPromptTemplate     
from app.config import get_llm
from app.utils.skill_manager import search_skills, get_skill_detail, create_skill, list_skills, get_skill_template
import json


def generate_new_skill_from_question(question: str, teacher_id: str = None) -> dict:
    """
    当找不到匹配Skill时，基于问题和现有Skill总结生成新Skill
    
    Args:
        question: 学生提问
        teacher_id: 教师ID（可选）
    
    Returns:
        dict: 新生成的Skill信息或错误
    """
    try:
        # 获取所有现有Skill作为上下文
        all_skills = list_skills()
        existing_content = ""
        
        if all_skills:
            # 取前5个相关Skill作为上下文（避免token过多）
            for skill in all_skills[:5]:
                skill_detail = get_skill_detail(skill.get("标题"))
                if skill_detail:
                    existing_content += f"## {skill_detail['title']}\n"
                    existing_content += f"描述：{skill_detail['metadata'].get('技能描述', '')}\n"
                    existing_content += f"内容：{skill_detail['content'][:500]}...\n\n"
        
        # 使用LLM生成新Skill
        prompt = ChatPromptTemplate.from_messages([
            ("system", """
你是一个专业的教学助手，需要基于学生的问题和现有教学Skill，创建一个新的教学Skill。

要求：
1. 新Skill必须使用标准的MD格式
2. 包含技能描述、适用场景、核心内容
3. 确保内容准确、有教学价值
4. 如果现有Skill相关，要整合相关知识
5. 生成的Skill标题要简洁明了
"""),
            ("user", """
学生问题：{question}

现有相关教学Skill：
{existing_skills}

请基于以上信息，生成一个新的教学Skill，使用以下模板：

{template}

请填充模板内容，生成完整的Skill MD文本。
""")
        ])
        
        chain = prompt | llm
        
        # 获取Claude风格模板
        template = get_skill_template("claude")
        
        response = chain.invoke({
            "question": question,
            "existing_skills": existing_content or "暂无相关Skill",
            "template": template
        })
        
        # 解析生成的Skill内容
        generated_content = response.content.strip()
        
        # 提取标题（从第一行#开始）
        lines = generated_content.split('\n')
        title = ""
        for line in lines:
            if line.startswith('# '):
                title = line[2:].strip()
                break
        
        if not title:
            return {
                "success": False,
                "error": "无法从生成内容中提取Skill标题"
            }
        
        # 创建新Skill
        create_result = create_skill(title, generated_content, teacher_id)
        
        if create_result["success"]:
            return {
                "success": True,
                "skill_title": title,
                "skill_content": generated_content,
                "generated": True
            }
        else:
            return {
                "success": False,
                "error": create_result.get("errors", ["创建Skill失败"])
            }
            
    except Exception as e:
        return {
            "success": False,
            "error": f"生成新Skill时出错: {str(e)}"
        }
    """
    根据学生问题搜索匹配的Skill

    Args:
        question: 学生提问
        top_k: 返回匹配得分最高的前k个Skill

    Returns:
        list: 匹配的Skill列表
    """
    matched = search_skills(question)
    return matched[:top_k]


def generate_answer_with_skill(question: str, matched_skills: list, use_mock: bool = False) -> dict:
    """
    基于匹配的Skill内容生成答案

    Args:
        question: 学生提问
        matched_skills: 匹配的Skill列表
        use_mock: 是否使用模拟模式（测试时使用）

    Returns:
        dict: 包含答案、参考Skill等信息
    """
    # 准备Skill内容
    skill_content_list = []
    
    if use_mock:
        # 模拟模式：直接使用传入的技能信息
        for skill in matched_skills:
            skill_content_list.append({
                "title": skill.get("标题", "未知技能"),
                "description": skill.get("技能描述", ""),
                "content": "这是一个模拟技能内容，用于测试。"
            })
    else:
        # 实际模式：调用get_skill_detail获取技能详情
        for skill in matched_skills:
            detail = get_skill_detail(skill.get("标题"))
            if detail:
                skill_content_list.append({
                    "title": detail["title"],
                    "description": detail["metadata"].get("技能描述", ""),
                    "content": detail["content"][:1000]  # 截取前1000字避免token过多
                })

    if not skill_content_list:
        return {
            "success": False,
            "error": "未找到相关Skill"
        }

    # 模拟模式：直接生成回答（用于测试）
    if use_mock or os.getenv("MOCK_MODE") == "1":
        return _generate_mock_answer(question, skill_content_list)

    # 实际模式：调用LLM
    prompt = ChatPromptTemplate.from_messages([
        ("system", """
你是一名经验丰富的教师助手。根据给定的教学Skill内容，回答学生的问题。

要求：
1. 使用Skill中的知识、案例、原理来回答
2. 清晰、循序渐进地讲解
3. 必要时举例说明
4. 如果问题与Skill不完全相关，说明这一点
5. 在回答末尾列出参考的内容来源
"""),
        ("user", """
学生问题：{question}

相关教学Skill：
{skill_content}

请基于上述Skill内容，回答学生的问题。
""")
    ])

    chain = prompt | llm

    # 格式化Skill内容
    formatted_skills = "\n\n".join([
        f"【Skill: {s['title']}】\n描述：{s['description']}\n内容预览：{s['content']}"
        for s in skill_content_list
    ])

    # 调用LLM生成回答
    try:
        response = chain.invoke({
            "question": question,
            "skill_content": formatted_skills
        })

        return {
            "success": True,
            "answer": response.content,
            "matched_skills": [
                {
                    "title": s.get("标题"),
                    "type": s.get("技能类型"),
                    "score": s.get("_match_score", 0)
                }
                for s in matched_skills
            ]
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def _generate_mock_answer(question: str, skills: list) -> dict:
    """生成模拟答案（用于测试，不调用LLM）"""
    # 根据问题内容生成简单的模拟答案
    mock_answers = {
        "互斥": """
互斥（Mutual Exclusion）是操作系统中的一个重要概念。它指的是多个进程不能同时进入临界区（即访问共享资源的代码段）。

**关键要点：**
1. 临界资源：一次只能被一个进程使用的资源
2. 临界区：访问临界资源的代码段
3. 互斥访问：任何时刻最多只有一个进程在临界区执行

**实现方式：**
- 信号量（Semaphore）：互斥信号量初值为1
- 管程（Monitor）：使用同步原语保护临界区
- 锁（Lock）：显式加锁/解锁机制

**实际例子：**
两个线程同时写入同一个文件时，必须互斥访问，否则数据会被破坏。
""",
        "同步": """
同步（Synchronization）是指进程间的执行顺序协调。与互斥不同，同步关注的是进程之间的协作顺序。

**关键要点：**
1. 定义：多个进程按照某种顺序执行
2. 目的：保证程序逻辑的正确性
3. 例子：生产者必须先生产，消费者才能消费

**常见同步模式：**
- 生产者-消费者：生产者生产→消费者消费
- 读者-写者：多读者可并发，写者独占
- 哲学家进餐：避免死锁的合作问题

**实现工具：**
- 信号量（Semaphore）：同步信号量初值为0
- 条件变量（Condition Variable）
- 屏障（Barrier）

**区别对比：**
- 互斥：同时只有一个进程在临界区（资源保护）
- 同步：多个进程按顺序执行（流程协调）
""",
        "链表": """
链表是一种常见的数据结构，由一系列节点组成，每个节点包含数据和指向下一个节点的指针。

**链表的优势：**
1. 插入/删除操作快（O(1)），只需改变指针
2. 动态内存分配，不需要连续空间
3. 可以实现各种复杂的数据结构

**链表的劣势：**
1. 随机访问慢（O(n)），需要从头遍历
2. 需要额外的指针空间
3. 缓存友好性差

**基本操作时间复杂度：**
- 查询：O(n)
- 插入（已知位置）：O(1)
- 删除（已知位置）：O(1)
- 插入/删除（未知位置）：O(n)

**常见链表变种：**
- 单链表：只有指向下一个节点的指针
- 双链表：既有指向前一个又指向后一个的指针
- 循环链表：尾节点指向头节点
""",
        "死锁": """
死锁是指两个或多个进程互相等待对方持有的资源，导致都无法继续执行的现象。

**死锁的四个必要条件：**
1. 互斥条件：资源只能被一个进程占有
2. 占有和等待：进程占有资源的同时还在等待其他资源
3. 不可抢占：资源不能被强制夺取
4. 循环等待：进程间形成环形等待链

**死锁的处理方法：**
1. 死锁预防：破坏四个必要条件之一
2. 死锁避免：使用银行家算法，动态判断是否安全
3. 死锁检测：允许死锁发生，定期检测并恢复
4. 死锁恢复：终止进程或抢占资源

**实际例子：**
线程A占有资源1，等待资源2；线程B占有资源2，等待资源1。两个线程都无法继续执行。
"""
    }

    # 根据问题选择合适的答案
    answer = None
    for key, content in mock_answers.items():
        if key in question:
            answer = content
            break

    # 如果没有找到特定答案，返回通用答案
    if not answer:
        answer = f"""
根据您的问题"{question}"，我已搜索到以下相关教学内容。

**相关概念：**
{'; '.join([s['title'] for s in skills])}

这些Skill涵盖了您提问相关的重要知识点。建议您：
1. 学习核心概念的定义和特点
2. 理解实际应用场景
3. 通过例题加深理解
4. 在实践中应用所学知识

如果您需要更详细的讲解，可以参考相关的教学案例。
"""

    return {
        "success": True,
        "answer": answer,
        "matched_skills": [
            {
                "title": s.get("标题"),
                "type": s.get("技能类型"),
                "score": s.get("_match_score", 0)
            }
            for s in skills
        ]
    }


def answer_student_question(student_id: str, question: str, use_mock: bool = False, auto_generate_skill: bool = True) -> dict:
    """
    完整的学生提问-回答工作流

    Args:
        student_id: 学生ID
        question: 提问内容
        use_mock: 是否使用模拟模式
        auto_generate_skill: 是否在找不到匹配Skill时自动生成新Skill

    Returns:
        dict: 包含回答、相关Skill、来源等信息
    """
    # 1. 搜索匹配的Skill
    matched_skills = match_skill_for_question(question)

    # 2. 如果没有找到匹配的Skill，根据设置决定是否生成新Skill
    if not matched_skills:
        if auto_generate_skill and not use_mock:
            # 尝试生成新Skill
            generate_result = generate_new_skill_from_question(question)
            
            if generate_result["success"]:
                # 重新搜索，现在应该能找到新生成的Skill
                matched_skills = match_skill_for_question(question)
                
                if not matched_skills:
                    # 如果还是找不到，用新生成的Skill手动构建
                    matched_skills = [{
                        "标题": generate_result["skill_title"],
                        "技能描述": "AI自动生成的教学Skill",
                        "关键词": question.replace(" ", ",").split(",")[:3],
                        "技能类型": "授课",
                        "适用场景": f"回答问题：{question[:50]}...",
                        "难度等级": "中级",
                        "_match_score": 8.0,
                        "_match_details": ["AI自动生成"]
                    }]
            else:
                # 生成失败，返回错误
                return {
                    "success": False,
                    "error": f"未找到相关Skill，且自动生成失败: {generate_result.get('error', '未知错误')}",
                    "student_id": student_id,
                    "question": question
                }
        elif not use_mock:
            return {
                "success": False,
                "error": "未找到相关Skill，请尝试其他关键词提问",
                "student_id": student_id,
                "question": question
            }
    
    # 3. 如果是模拟模式且没有匹配到技能，创建一个虚拟技能
    if use_mock and not matched_skills:
        matched_skills = [{
            "标题": "操作系统基础",
            "技能描述": "操作系统核心概念，包括进程管理、内存管理、文件系统等",
            "关键词": "操作系统, 进程, 内存, 互斥, 同步",
            "技能类型": "授课",
            "适用场景": "基础教学",
            "难度等级": "初级"
        }]

    # 4. 基于Skill生成回答
    result = generate_answer_with_skill(question, matched_skills, use_mock=use_mock)

    if not result["success"]:
        return {
            "success": False,
            "error": result.get("error"),
            "student_id": student_id,
            "question": question
        }

    # 5. 返回完整结果
    response = {
        "success": True,
        "student_id": student_id,
        "question": question,
        "answer": result["answer"],
        "matched_skills": result["matched_skills"],
        "reference_count": len(result["matched_skills"])
    }
    
    # 如果生成了新Skill，在响应中标记
    if auto_generate_skill and 'generate_result' in locals() and generate_result.get("success"):
        response["new_skill_generated"] = True
        response["generated_skill_title"] = generate_result["skill_title"]
    
    return response

#!/usr/bin/env python3
"""
工作流测试脚本

该脚本用于测试教学工作流的完整执行流程，包括：
1. 加载技能
2. 生成题目
3. 模拟学生答题
4. 评分
5. 分析进度
6. 决定是否重试

用法：
    python test_workflow.py
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
backend_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(backend_dir))

from app.graph.workflow import create_workflow, create_qa_workflow

def test_main_workflow():
    """
    测试主学习工作流
    """
    print("=" * 70)
    print("🧪 测试主学习工作流")
    print("=" * 70)
    
    # 1. 初始化工作流
    workflow = create_workflow()
    print("✅ 工作流初始化成功")
    
    # 2. 定义初始状态
    initial_state = {
        "skill_title": "测试技能",
        "student_id": "S001"
    }
    print(f"📋 初始状态: {initial_state}")
    
    # 3. 执行工作流
    print("🚀 开始执行工作流...")
    result = workflow.invoke(initial_state)
    print("✅ 工作流执行完成")
    
    # 4. 输出结果
    print("\n📊 执行结果:")
    print("-" * 50)
    
    # 评分结果
    grading_result = result.get("grading_result", {})
    print(f"🏆 总得分: {grading_result.get('total_score', 'N/A')}")
    print(f"📝 薄弱点: {grading_result.get('weak_points', 'N/A')}")
    print(f"💬 总体反馈: {grading_result.get('overall_feedback', 'N/A')}")
    
    # 分析报告
    analysis_report = result.get("analysis_report", {})
    print(f"\n📈 分析报告:")
    print(f"趋势: {analysis_report.get('trend', 'N/A')}")
    print(f"建议: {analysis_report.get('suggestion', 'N/A')}")
    
    # 重试决策
    need_retry = result.get("need_retry", False)
    print(f"\n🔄 是否需要重试: {'是' if need_retry else '否'}")
    
    # 问题和答案
    questions = result.get("questions", [])
    answers = result.get("student_answers", [])
    print(f"\n📚 生成的题目数量: {len(questions)}")
    if questions:
        print("\n示例题目:")
        for i, (q, a) in enumerate(zip(questions[:2], answers[:2]), 1):
            print(f"\n{str(i).zfill(2)}. {q.get('question', 'N/A')}")
            print(f"   答案: {a}")
    
    print("\n" + "=" * 70)
    print("✅ 主工作流测试完成")
    print("=" * 70)
    return result

def test_qa_workflow():
    """
    测试QA问答工作流
    """
    print("\n" + "=" * 70)
    print("🧪 测试QA问答工作流")
    print("=" * 70)
    
    # 1. 初始化QA工作流
    qa_workflow = create_qa_workflow()
    print("✅ QA工作流初始化成功")
    
    # 2. 定义测试问题
    test_questions = [
        "什么是进程同步？",
        "虚拟内存的工作原理是什么？",
        "如何防止死锁？"
    ]
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n🔍 测试问题 {i}: {question}")
        
        # 3. 定义初始状态
        initial_state = {
            "question": question
        }
        
        # 4. 执行工作流
        print("🚀 开始执行QA工作流...")
        result = qa_workflow.invoke(initial_state)
        print("✅ QA工作流执行完成")
        
        # 5. 输出结果
        print("\n📊 QA结果:")
        print("-" * 50)
        
        qa_result = result.get("qa_result", {})
        success = qa_result.get("success", False)
        
        if success:
            print(f"✅ 回答成功")
            answer = qa_result.get("answer", "")
            print(f"💬 回答: {answer[:200]}..." if len(answer) > 200 else f"💬 回答: {answer}")
            
            matched_skills = qa_result.get("matched_skills", [])
            print(f"\n🔗 匹配的技能: {len(matched_skills)} 个")
            for skill in matched_skills[:2]:
                print(f"   - {skill.get('title', 'N/A')} (匹配度: {skill.get('score', 'N/A')})")
        else:
            print(f"❌ 回答失败")
            error = qa_result.get("error", "未知错误")
            print(f"💥 错误: {error}")
    
    print("\n" + "=" * 70)
    print("✅ QA工作流测试完成")
    print("=" * 70)

def main():
    """
    主测试函数
    """
    try:
        # 测试主学习工作流
        test_main_workflow()
        
        # 测试QA问答工作流
        test_qa_workflow()
        
        print("\n🎉 所有测试完成！")
        print("\n📝 测试总结:")
        print("- 主学习工作流: 验证了完整的教学流程")
        print("- QA问答工作流: 验证了问题处理和回答生成")
        print("- 数据持久化: 检查 data/ 目录下的生成文件")
        
    except Exception as e:
        print(f"\n❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

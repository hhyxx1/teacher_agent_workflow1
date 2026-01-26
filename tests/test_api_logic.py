import os
import sys
import asyncio
from unittest.mock import MagicMock, patch

# 将项目根目录和 backend 目录添加到路径
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(project_root)

async def run_test():
    print("=== 开始测试 Skill 匹配与问答逻辑 (Mock 模式) ===\n")
    
    # 模拟 LLM 响应
    mock_llm = MagicMock()
    
    # 设置匹配逻辑的模拟返回
    def mock_invoke(prompt):
        response = MagicMock()
        
        # 1. 区分是“搜索匹配”还是“生成回答”
        is_search = "可选技能列表" in prompt
        
        if is_search:
            # 搜索匹配逻辑：必须从“学生提问:”这一行来判断
            if "学生提问: \"老师，我不太明白进程同步和互斥" in prompt:
                response.content = "process_synchronization_mutex"
            elif "学生提问: \"什么是死锁？" in prompt:
                response.content = "deadlock_prevention_detection"
            elif "学生提问: \"虚拟内存" in prompt:
                response.content = "virtual_memory_paging"
            else:
                response.content = "None"
        else:
            # 生成回答逻辑
            response.content = "这是一个模拟的专业教师回答。我已经参考了相关的教学技能文档，建议您重点关注该知识点的核心原理和实际应用案例。"
            
        return response

    mock_llm.invoke.side_effect = mock_invoke

    # 在 patch 环境下导入和运行
    with patch("config.get_llm", return_value=mock_llm):
        # 延迟导入，确保 patch 生效
        from backend.app.services.skill_service import SkillService
        from backend.app.models.qa import QuestionRequest
        from backend.app.api.qa import ask_question

        service = SkillService(skills_dir=os.path.join(project_root, "skills"))
        
        # 测试用例
        test_cases = [
            "老师，我不太明白进程同步和互斥的区别是什么？",
            "什么是死锁？怎么预防它？",
            "虚拟内存的分页机制是怎么工作的？",
            "今天天气怎么样？"
        ]
        
        for i, query in enumerate(test_cases, 1):
            print(f"测试用例 {i}: {query}")
            
            # 1. 测试匹配逻辑
            match_id = service.find_best_match(query)
            print(f"  -> 匹配到的 Skill ID: {match_id}")
            
            # 2. 测试完整问答逻辑
            request = QuestionRequest(student_id="test_student", question=query)
            response = await ask_question(request)
            
            if response.success:
                print(f"  -> 回答预览: {response.answer[:100]}...")
            else:
                print(f"  -> 错误: {response.error}")
            print("-" * 50)

if __name__ == "__main__":
    asyncio.run(run_test())

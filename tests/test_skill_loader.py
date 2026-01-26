"""
技能加载器测试
"""

import os
import tempfile
import pytest
from utils.skill_manager import load_skill, discover_skills


# 创建测试技能文件
def create_test_skill_file(skill_dir, skill_name, content):
    """
    创建测试技能文件
    """
    os.makedirs(skill_dir, exist_ok=True)
    file_path = os.path.join(skill_dir, f"{skill_name}.md")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    return file_path


def create_test_skill_directory(skill_dir, skill_name, content):
    """
    创建测试技能目录（标准SKILL.md格式）
    """
    skill_dir_path = os.path.join(skill_dir, skill_name)
    os.makedirs(skill_dir_path, exist_ok=True)
    file_path = os.path.join(skill_dir_path, "SKILL.md")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    return file_path


class TestSkillLoader:
    """
    技能加载器测试
    """
    
    def setup_method(self):
        """
        设置测试环境
        """
        self.temp_dir = tempfile.mkdtemp()
    
    def teardown_method(self):
        """
        清理测试环境
        """
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_load_traditional_skill(self):
        """
        测试加载传统格式技能
        """
        # 创建传统格式技能文件
        content = """
# 同步与互斥教学案例

## 元数据
- 技能类型：授课
- 适用场景：操作系统课程
- 难度等级：中级

## 内容
### 1. 同步与互斥的基本概念
同步是指进程之间的协作关系，互斥是指进程之间的竞争关系。

### 2. 临界区问题
临界区是指进程中访问共享资源的代码段。
        """
        
        create_test_skill_file(self.temp_dir, "同步与互斥教学案例", content)
        
        # 加载技能
        skill = load_skill("同步与互斥教学案例", self.temp_dir)
        
        # 验证结果
        assert skill['name'] == "同步与互斥教学案例"
        assert skill['title'] == "同步与互斥教学案例"
        assert skill['metadata']['技能类型'] == "授课"
        assert "同步是指进程之间的协作关系" in skill['content']
    
    def test_load_standard_skill(self):
        """
        测试加载标准SKILL.md格式技能
        """
        # 创建标准格式技能文件
        content = """
# Paper Review

结构化的学术论文评审框架

## When to Use
- 学生需要分析学术论文
- 教师需要评审学生的论文
- 研究人员需要快速了解论文内容

## Process
1. 阅读论文摘要和引言
2. 分析研究方法
3. 评估实验结果
4. 总结贡献和不足
5. 提供改进建议
        """
        
        create_test_skill_directory(self.temp_dir, "paper_review", content)
        
        # 加载技能
        skill = load_skill("paper_review", self.temp_dir)
        
        # 验证结果
        assert skill['name'] == "Paper Review"
        assert skill['title'] == "paper_review"
        assert skill['description'] == "结构化的学术论文评审框架"
        assert len(skill['when_to_use']) > 0
        assert "学生需要分析学术论文" in skill['when_to_use']
        assert "阅读论文摘要和引言" in skill['content']
    
    def test_discover_skills(self):
        """
        测试自动发现技能
        """
        # 创建传统格式技能
        traditional_content = """
# 同步与互斥教学案例

## 元数据
- 技能类型：授课

## 内容
同步是指进程之间的协作关系
        """
        create_test_skill_file(self.temp_dir, "同步与互斥教学案例", traditional_content)
        
        # 创建标准格式技能
        standard_content = """
# Paper Review

结构化的学术论文评审框架

## When to Use
- 学生需要分析学术论文
        """
        create_test_skill_directory(self.temp_dir, "paper_review", standard_content)
        
        # 发现技能
        skills = discover_skills(self.temp_dir)
        
        # 验证结果
        assert len(skills) == 2
        skill_names = [skill['name'] for skill in skills]
        assert "同步与互斥教学案例" in skill_names
        assert "Paper Review" in skill_names
    
    def test_load_nonexistent_skill(self):
        """
        测试加载不存在的技能
        """
        with pytest.raises(FileNotFoundError):
            load_skill("nonexistent_skill", self.temp_dir)

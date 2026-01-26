"""
Skill 加载器
负责读取本地 Markdown 格式的教学 Skill 文件，并解析元数据和内容。
支持标准 SKILL.md 格式（OpenSkills/Claude Skills）和传统格式。
"""

import os
import re
from typing import Dict, List
from config import SKILL_DIR

def load_skill(skill_title: str, skill_dir: str = SKILL_DIR) -> Dict:
    """
    加载 Markdown 格式的 Skill 文件
    
    支持两种格式：
    1. 标准 SKILL.md 格式（OpenSkills/Claude Skills）
    2. 传统格式（## 元数据 + ## 内容）
    
    Args:
        skill_title (str): Skill 文件名（不含 .md 后缀）或目录名
        skill_dir (str): 存放 Skill 文件的目录路径，默认为 config.py 中定义的目录
        
    Returns:
        Dict: 包含 name, title, description, metadata, content, when_to_use 的字典
    """
    # 尝试作为目录加载（标准 SKILL.md 格式）
    skill_dir_path = os.path.join(skill_dir, skill_title)
    skill_file_path = os.path.join(skill_dir, f"{skill_title}.md")
    
    # 确定实际的文件路径
    if os.path.isdir(skill_dir_path):
        # 标准格式：目录包含 SKILL.md 文件
        actual_file_path = os.path.join(skill_dir_path, "SKILL.md")
    else:
        # 传统格式：直接是 .md 文件
        actual_file_path = skill_file_path
    
    if not os.path.exists(actual_file_path):
        raise FileNotFoundError(f"Skill 文件未找到: {actual_file_path}")
        
    with open(actual_file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 提取技能名称（从标题）
    name_match = re.search(r"^#\s+(.*?)$", content, re.MULTILINE)
    name = name_match.group(1).strip() if name_match else skill_title

    # 提取简短描述（标题后的前1-2行）
    lines = content.split("\n")
    description = ""
    for i, line in enumerate(lines):
        if i > 0 and line.strip() and not line.startswith("#"):
            description = line.strip()
            break

    # 尝试解析标准 SKILL.md 格式
    when_to_use = []
    process_structure = ""
    
    # 提取 When to Use 部分
    when_match = re.search(r"##\s*When to Use\n(.*?)(?=##|$)", content, re.DOTALL)
    if when_match:
        when_content = when_match.group(1).strip()
        # 提取项目符号列表
        when_items = re.findall(r"-\s+(.*?)(?=-|$)", when_content, re.DOTALL)
        when_to_use = [item.strip() for item in when_items]
    
    # 提取 Process/Structure 部分
    process_match = re.search(r"##\s*(?:Process|Structure|Instructions)\n(.*?)(?=##|$)", content, re.DOTALL)
    if process_match:
        process_structure = process_match.group(1).strip()

    # 尝试解析传统格式（向后兼容）
    metadata = {}
    content_part = ""
    
    # 1. 提取元数据（## 元数据 到 ## 之间的内容）
    meta_match = re.search(r"## 元数据\n(.*?)\n##", content, re.DOTALL)
    if meta_match:
        meta_lines = meta_match.group(1).strip().split("\n")
        for line in meta_lines:
            if line.startswith("- "):
                # 解析 "- Key：Value" 格式
                key_val = line[2:].split("：", 1)
                if len(key_val) == 2:
                    metadata[key_val[0].strip()] = key_val[1].strip()

    # 2. 提取正文内容（## 内容 之后的所有文本）
    if "## 内容" in content:
        content_part = re.split(r"## 内容", content)[1].strip()
    elif process_structure:
        # 如果是标准格式，使用 Process/Structure 部分作为内容
        content_part = process_structure
    else:
        # 否则使用整个文件内容（除了标题）
        content_part = "\n".join([line for line in lines[1:] if line]).strip()
    
    return {
        "name": name,
        "title": skill_title,
        "description": description,
        "metadata": metadata,
        "content": content_part,
        "when_to_use": when_to_use
    }

def discover_skills(skill_dir: str = SKILL_DIR) -> List[Dict]:
    """
    自动发现和加载目录中的所有技能
    
    Args:
        skill_dir (str): 存放 Skill 文件的目录路径
        
    Returns:
        List[Dict]: 技能列表
    """
    skills = []
    
    if not os.path.exists(skill_dir):
        return skills
    
    # 遍历目录
    for item in os.listdir(skill_dir):
        item_path = os.path.join(skill_dir, item)
        
        if os.path.isdir(item_path):
            # 标准格式：目录包含 SKILL.md 文件
            skill_file = os.path.join(item_path, "SKILL.md")
            if os.path.exists(skill_file):
                try:
                    skill_data = load_skill(item, skill_dir)
                    skills.append(skill_data)
                except Exception as e:
                    print(f"加载技能 {item} 失败: {e}")
        elif item.endswith(".md"):
            # 传统格式：直接是 .md 文件
            skill_name = item[:-3]  # 移除 .md 后缀
            try:
                skill_data = load_skill(skill_name, skill_dir)
                skills.append(skill_data)
            except Exception as e:
                print(f"加载技能 {skill_name} 失败: {e}")
    
    return skills


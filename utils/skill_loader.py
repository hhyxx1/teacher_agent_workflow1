"""
Skill 加载器
负责读取本地 Markdown 格式的教学 Skill 文件，并解析元数据和内容。
"""

import os
import re
from typing import Dict
from config import SKILL_DIR

def load_skill(skill_title: str, skill_dir: str = SKILL_DIR) -> Dict:
    """
    加载 Markdown 格式的 Skill 文件
    
    文件格式约定：
    ------------------------
    ## 元数据
    - 键：值
    ## 内容
    这里是正文...
    ------------------------
    
    Args:
        skill_title (str): Skill 文件名（不含 .md 后缀）
        skill_dir (str): 存放 Skill 文件的目录路径，默认为 config.py 中定义的目录
        
    Returns:
        Dict: 包含 title, metadata, content 的字典
    """
    skill_path = os.path.join(skill_dir, f"{skill_title}.md")
    
    if not os.path.exists(skill_path):
        raise FileNotFoundError(f"Skill 文件未找到: {skill_path}")
        
    with open(skill_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. 提取元数据（## 元数据 到 ## 之间的内容）
    metadata = {}
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
    content_part = re.split(r"## 内容", content)[1].strip() if "## 内容" in content else ""
    
    return {
        "title": skill_title,
        "metadata": metadata,
        "content": content_part
    }


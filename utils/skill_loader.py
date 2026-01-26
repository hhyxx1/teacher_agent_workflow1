"""
Skill 加载器
负责读取本地 Markdown 格式的教学 Skill 文件，并解析元数据和内容。
"""

import os
import re
import yaml # 尝试导入 yaml 处理 frontmatter
from typing import Dict, List, Optional
from config import SKILL_DIR

def list_available_skills(skill_dir: str = SKILL_DIR) -> List[str]:
    """
    列出所有可用的 Skill 名称（不含后缀）
    """
    if not os.path.exists(skill_dir):
        return []
    return [f[:-3] for f in os.listdir(skill_dir) if f.endswith(".md")]

def load_skill(skill_title: str, skill_dir: str = SKILL_DIR) -> Dict:
    """
    加载并解析 Skill 文件
    
    支持两种格式：
    1. 带有 YAML Frontmatter 的标准格式
    2. 传统的以 ## 元数据 为标记的格式
    """
    skill_path = os.path.join(skill_dir, f"{skill_title}.md")
    
    if not os.path.exists(skill_path):
        # 这里预留给未来的“自动生成”逻辑
        raise FileNotFoundError(f"Skill '{skill_title}' 不存在。")
        
    with open(skill_path, "r", encoding="utf-8") as f:
        raw_content = f.read()

    metadata = {}
    content_body = raw_content

    # 优先尝试解析 YAML Frontmatter (--- ... ---)
    frontmatter_match = re.match(r"^---\n(.*?)\n---\n", raw_content, re.DOTALL)
    if frontmatter_match:
        yaml_text = frontmatter_match.group(1)
        # 简单解析 YAML（避免强制依赖 PyYAML）
        for line in yaml_text.split("\n"):
            if ":" in line:
                k, v = line.split(":", 1)
                metadata[k.strip()] = v.strip().strip("[]'\"")
        content_body = raw_content[frontmatter_match.end():].strip()
    
    # 如果没有 Frontmatter，尝试解析传统的 ## 元数据 格式
    if not metadata:
        meta_match = re.search(r"## 元数据\n(.*?)\n##", raw_content, re.DOTALL)
        if meta_match:
            meta_lines = meta_match.group(1).strip().split("\n")
            for line in meta_lines:
                if line.startswith("- "):
                    key_val = line[2:].split("：", 1)
                    if len(key_val) == 2:
                        metadata[key_val[0].strip()] = key_val[1].strip()
        
        # 提取正文内容
        content_parts = re.split(r"## 内容", raw_content)
        if len(content_parts) > 1:
            content_body = content_parts[1].strip()

    return {
        "title": skill_title,
        "metadata": metadata,
        "content": content_body
    }


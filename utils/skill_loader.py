import os
import re
from typing import Dict

def load_skill(skill_title: str, skill_dir: str = "skills") -> Dict:
    """加载MD格式Skill，返回元数据+内容"""
    skill_path = os.path.join(skill_dir, f"{skill_title}.md")
    with open(skill_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 提取元数据
    metadata = {}
    meta_match = re.search(r"## 元数据\n(.*?)\n##", content, re.DOTALL)
    if meta_match:
        meta_lines = meta_match.group(1).strip().split("\n")
        for line in meta_lines:
            if line.startswith("- "):
                key_val = line[2:].split("：", 1)
                if len(key_val) == 2:
                    metadata[key_val[0].strip()] = key_val[1].strip()

    # 提取内容
    content_part = re.split(r"## 内容", content)[1].strip() if "## 内容" in content else ""
    return {
        "title": skill_title,
        "metadata": metadata,
        "content": content_part
    }


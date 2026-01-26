"""
Skill 管理模块
负责 Skill 的创建、验证、搜索、复用等功能
"""
import os
import json
import re
from typing import Dict, List, Optional
from datetime import datetime
from config import SKILL_DIR, DATA_DIR

# Skill索引文件路径
SKILL_INDEX_PATH = os.path.join(DATA_DIR, "skill_index.json")

def get_skill_template() -> str:
    """生成Skill MD模板"""
    template = """# {Skill标题}

## 技能描述
{一句话描述这个skill的用途}

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
{FAQ列表}

## 参考资料
- 资料1
- 资料2
"""
    return template


def parse_skill_metadata(content: str) -> Dict:
    """从MD内容中提取元数据"""
    metadata = {}

    # 提取技能描述
    desc_match = re.search(r"## 技能描述\n(.*?)\n", content, re.DOTALL)
    if desc_match:
        metadata["技能描述"] = desc_match.group(1).strip()

    # 提取元数据部分
    meta_match = re.search(r"## 元数据\n(.*?)\n##", content, re.DOTALL)
    if meta_match:
        meta_lines = meta_match.group(1).strip().split("\n")
        for line in meta_lines:
            if line.startswith("- "):
                parts = line[2:].split("：", 1)
                if len(parts) == 2:
                    key, value = parts[0].strip(), parts[1].strip()
                    metadata[key] = value

    # 提取标题
    title_match = re.match(r"# (.*?)\n", content)
    if title_match:
        metadata["标题"] = title_match.group(1).strip()

    return metadata


def validate_skill(content: str) -> Dict:
    """验证Skill格式是否符合规范"""
    errors = []
    warnings = []

    required_sections = ["# ", "## 技能描述", "## 元数据", "## 内容"]
    for section in required_sections:
        if section not in content:
            errors.append(f"缺少必需部分: {section}")

    metadata = parse_skill_metadata(content)
    required_fields = ["技能类型", "适用场景", "关键词"]
    for field in required_fields:
        if field not in metadata or not metadata[field]:
            warnings.append(f"元数据缺少推荐字段: {field}")

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "metadata": metadata
    }


def create_skill(title: str, content: str, teacher_id: str) -> Dict:
    """创建新的Skill"""
    # 验证格式
    validation = validate_skill(content)
    if not validation["valid"]:
        return {
            "success": False,
            "errors": validation["errors"]
        }

    # 添加创建时间和创建者
    metadata = validation["metadata"]
    if "创建者" not in metadata:
        content = content.replace("{教师ID}", teacher_id)
    if "创建时间" not in metadata:
        content = content.replace("{YYYY-MM-DD}", datetime.now().strftime("%Y-%m-%d"))

    # 保存文件
    os.makedirs(SKILL_DIR, exist_ok=True)
    skill_path = os.path.join(SKILL_DIR, f"{title}.md")

    if os.path.exists(skill_path):
        return {
            "success": False,
            "errors": [f"Skill '{title}' 已存在"]
        }

    with open(skill_path, "w", encoding="utf-8") as f:
        f.write(content)

    # 更新索引
    _update_skill_index(title, metadata)

    return {
        "success": True,
        "skill_title": title,
        "warnings": validation.get("warnings", [])
    }


def list_skills(skill_type: Optional[str] = None, keywords: Optional[List[str]] = None) -> List[Dict]:
    """列出所有Skill，可按类型和关键词筛选"""
    index = _load_skill_index()
    skills = []

    for skill in index:
        # 类型筛选
        if skill_type and skill.get("技能类型") != skill_type:
            continue

        # 关键词筛选
        if keywords:
            skill_keywords = skill.get("关键词", "").split(",")
            skill_keywords = [k.strip().lower() for k in skill_keywords]
            if not any(kw.lower() in skill_keywords for kw in keywords):
                continue

        skills.append(skill)

    return skills


def search_skills(query: str) -> List[Dict]:
    """搜索Skill（关键词匹配）"""
    index = _load_skill_index()
    query_lower = query.lower()
    matched_skills = []

    for skill in index:
        score = 0

        # 标题匹配（权重最高）
        if query_lower in skill.get("标题", "").lower():
            score += 10

        # 描述匹配
        if query_lower in skill.get("技能描述", "").lower():
            score += 5

        # 关键词匹配
        keywords = skill.get("关键词", "").split(",")
        for kw in keywords:
            if query_lower in kw.strip().lower():
                score += 3

        # 场景匹配
        if query_lower in skill.get("适用场景", "").lower():
            score += 2

        if score > 0:
            skill_with_score = skill.copy()
            skill_with_score["_match_score"] = score
            matched_skills.append(skill_with_score)

    # 按匹配分数排序
    matched_skills.sort(key=lambda x: x["_match_score"], reverse=True)
    return matched_skills


def fork_skill(original_title: str, new_title: str, teacher_id: str, modifications: Optional[str] = None) -> Dict:
    """复用(fork)现有Skill"""
    original_path = os.path.join(SKILL_DIR, f"{original_title}.md")

    if not os.path.exists(original_path):
        return {
            "success": False,
            "errors": [f"原Skill '{original_title}' 不存在"]
        }

    # 读取原内容
    with open(original_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 修改标题
    content = re.sub(r"# .*?\n", f"# {new_title}\n", content, count=1)

    # 添加fork信息
    fork_info = f"\n> **Fork自**: {original_title} by {teacher_id} on {datetime.now().strftime('%Y-%m-%d')}\n"
    content = content.replace("## 技能描述", fork_info + "\n## 技能描述")

    # 应用修改
    if modifications:
        content += f"\n\n## 定制修改\n{modifications}\n"

    # 保存为新Skill
    return create_skill(new_title, content, teacher_id)


def get_skill_detail(title: str) -> Optional[Dict]:
    """获取Skill完整信息"""
    skill_path = os.path.join(SKILL_DIR, f"{title}.md")

    if not os.path.exists(skill_path):
        return None

    with open(skill_path, "r", encoding="utf-8") as f:
        content = f.read()

    metadata = parse_skill_metadata(content)

    return {
        "title": title,
        "metadata": metadata,
        "content": content,
        "file_path": skill_path
    }


# ========== 内部辅助函数 ==========

def _load_skill_index() -> List[Dict]:
    """加载Skill索引"""
    if not os.path.exists(SKILL_INDEX_PATH):
        return []

    with open(SKILL_INDEX_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def _save_skill_index(index: List[Dict]):
    """保存Skill索引"""
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(SKILL_INDEX_PATH, "w", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False, indent=2)


def _update_skill_index(title: str, metadata: Dict):
    """更新索引中的单个Skill"""
    index = _load_skill_index()

    # 移除旧条目（如果存在）
    index = [s for s in index if s.get("标题") != title]

    # 添加新条目
    index_entry = {
        "标题": title,
        **metadata
    }
    index.append(index_entry)

    _save_skill_index(index)


def rebuild_skill_index():
    """重建整个Skill索引（扫描skills目录）"""
    index = []

    if not os.path.exists(SKILL_DIR):
        _save_skill_index(index)
        return

    for filename in os.listdir(SKILL_DIR):
        if filename.endswith(".md"):
            title = filename[:-3]  # 移除.md后缀
            skill_path = os.path.join(SKILL_DIR, filename)

            with open(skill_path, "r", encoding="utf-8") as f:
                content = f.read()

            metadata = parse_skill_metadata(content)
            index_entry = {
                "标题": title,
                **metadata
            }
            index.append(index_entry)

    _save_skill_index(index)
    print(f"✓ 索引已重建，共 {len(index)} 个Skill")

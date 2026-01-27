"""
Skill 管理模块
负责 Skill 的创建、加载、验证、搜索、复用等功能
"""
import os
import json
import re
from typing import Dict, List, Optional
from datetime import datetime
from app.config.settings import SKILL_DIR, DATA_DIR

# 技能类型管理
SKILL_TYPES = {
    "面试": {
        "description": "针对面试场景的技能",
        "keywords": ["面试", "interview", "求职", "招聘"]
    },
    "授课": {
        "description": "针对课堂教学的技能", 
        "keywords": ["教学", "授课", "课堂", "讲解"]
    },
    "代码分析": {
        "description": "针对代码分析的能力",
        "keywords": ["代码", "编程", "开发", "算法"]
    },
    "其他": {
        "description": "其他类型的技能",
        "keywords": []
    }
}

def validate_skill_type(skill_type: str) -> bool:
    """验证技能类型是否有效"""
    return skill_type in SKILL_TYPES

def get_skill_type_info(skill_type: str) -> Dict:
    """获取技能类型信息"""
    return SKILL_TYPES.get(skill_type, SKILL_TYPES["其他"])

def get_current_teacher_id(teacher_id: Optional[str] = None) -> str:
    """
    获取当前教师ID
    在实际应用中，这里应该从JWT token、session或其他认证机制中获取
    当前作为占位符实现
    """
    if teacher_id:
        return teacher_id
    
    # TODO: 实现真实的教师身份识别
    # 可能的实现方式：
    # 1. 从JWT token中解析
    # 2. 从session中获取  
    # 3. 从请求头中获取
    # 4. 从环境变量中获取（开发环境）
    
    import os
    return os.getenv("CURRENT_TEACHER_ID", "teacher_default")

# 导入技能加载相关功能（整合自skill_loader.py）
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

# 尝试解析标准格式和传统格式
    metadata = {}
    content_part = ""
    
    # 1. 提取Claude标准格式的各个部分
    if when_to_use:
        metadata["适用场景"] = "；".join(when_to_use)
    
    if process_structure:
        content_part = process_structure
        metadata["流程步骤"] = process_structure
    
    # 2. 提取Examples部分
    examples_match = re.search(r"## Examples\n(.*?)(?=##|$)", content, re.DOTALL)
    if examples_match:
        metadata["示例内容"] = examples_match.group(1).strip()
    
    # 3. 提取传统格式元数据（## 元数据 到 ## 之间的内容）
    meta_match = re.search(r"## 元数据\n(.*?)(?=##|$)", content, re.DOTALL)
    if meta_match:
        meta_lines = meta_match.group(1).strip().split("\n")
        for line in meta_lines:
            if line.startswith("-"):
                # 解析 "- Key：Value" 格式
                key_val = line[2:].split("：", 1)
                if len(key_val) == 2:
                    metadata[key_val[0].strip()] = key_val[1].strip()

    # 4. 提取正文内容（## 内容 之后的所有文本）
    if "## 内容" in content:
        content_part = re.split(r"## 内容", content)[1].strip()
    elif not content_part and process_structure:
        # 如果是标准格式，使用 Process/Structure 部分作为内容
        content_part = process_structure
    elif not content_part:
        # 否则使用整个文件内容（除了标题）
        content_part = "\n".join([line for line in lines[1:] if line]).strip()
    
    return {
        "name": name,
        "title": skill_title,
        "description": description,
        "metadata": metadata,
        "content": content_part,
        "when_to_use": when_to_use,
        "format_type": "claude" if when_to_use else "traditional"
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

# Skill索引文件路径
SKILL_INDEX_PATH = os.path.join(DATA_DIR, "skill_index.json")

def get_skill_template(template_type: str = "claude") -> str:
    """
    生成Skill MD模板，支持Claude标准格式和传统格式
    
    Args:
        template_type: "claude" 或 "traditional"
    
    Returns:
        str: 模板内容
    """
    if template_type == "claude":
        template = """# {Skill标题}

## 技能描述
{一句话描述这个skill的用途}

## When to Use
- {使用场景1}
- {使用场景2}
- {使用场景3}

## Process
{具体的步骤或流程说明}

## Examples
{示例内容或案例}

## 元数据
- 技能类型：面试/授课/代码分析/其他
- 难度等级：初级/中级/高级
- 关键词：keyword1, keyword2, keyword3
- 创建者：{教师ID}
- 创建时间：{YYYY-MM-DD}
"""
    else:  # traditional format
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
    """从MD内容中提取元数据，支持Claude标准格式和传统格式"""
    metadata = {}

    # 提取标题
    title_match = re.match(r"# (.*?)\n", content)
    if title_match:
        metadata["标题"] = title_match.group(1).strip()

    # 提取技能描述
    desc_match = re.search(r"## 技能描述\n(.*?)(?=\n##|\n$)", content, re.DOTALL)
    if not desc_match:
        # 尝试其他可能的描述格式
        desc_match = re.search(r"# (.*?)\n\n(.*?)(?=\n##|\n$)", content, re.DOTALL)
    
    if desc_match:
        description = desc_match.group(1).strip()
        # 只取第一行作为简短描述
        lines = description.split('\n')
        metadata["技能描述"] = lines[0] if lines else description

    # 提取When to Use（Claude标准格式）
    when_match = re.search(r"## When to Use\n(.*?)(?=\n##|\n$)", content, re.DOTALL)
    if when_match:
        when_content = when_match.group(1).strip()
        # 提取项目符号列表
        when_items = re.findall(r"-\s+(.*?)(?=-|$)", when_content, re.DOTALL)
        metadata["适用场景"] = "；".join([item.strip() for item in when_items])

    # 提取Process（Claude标准格式）
    process_match = re.search(r"## Process\n(.*?)(?=\n##|\n$)", content, re.DOTALL)
    if process_match:
        metadata["流程步骤"] = process_match.group(1).strip()

    # 提取Examples（Claude标准格式）
    examples_match = re.search(r"## Examples\n(.*?)(?=\n##|\n$)", content, re.DOTALL)
    if examples_match:
        metadata["示例内容"] = examples_match.group(1).strip()

    # 提取元数据部分（传统格式）
    meta_match = re.search(r"## 元数据\n(.*?)(?=\n##|\n$)", content, re.DOTALL)
    if meta_match:
        meta_lines = meta_match.group(1).strip().split("\n")
        for line in meta_lines:
            if line.startswith("- "):
                # 解析 "- Key：Value" 格式
                key_val = line[2:].split("：", 1)
                if len(key_val) == 2:
                    metadata[key_val[0].strip()] = key_val[1].strip()

    # 如果没有找到适用场景，尝试从传统格式的元数据中获取
    if "适用场景" not in metadata and "适用场景" in metadata:
        metadata["适用场景"] = metadata["适用场景"]

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


def create_skill(title: str, content: str, teacher_id: Optional[str] = None) -> Dict:
    """
    创建新的Skill
    
    Args:
        title: Skill标题
        content: Skill内容
        teacher_id: 教师ID（可选，如果不提供则自动获取）
    
    Returns:
        Dict: 创建结果
    """
    # 验证格式
    validation = validate_skill(content)
    if not validation["valid"]:
        return {
            "success": False,
            "errors": validation["errors"]
        }

    # 获取教师身份
    teacher_id = get_current_teacher_id(teacher_id)
    
    # 添加创建时间和创建者
    metadata = validation["metadata"]
    if "创建者" not in metadata:
        content = content.replace("{教师ID}", teacher_id)
    if "创建时间" not in metadata:
        content = content.replace("{YYYY-MM-DD}", datetime.now().strftime("%Y-%m-%d"))
    
    # 验证技能类型
    skill_type = metadata.get("技能类型", "其他")
    if not validate_skill_type(skill_type):
        return {
            "success": False,
            "errors": [f"无效的技能类型: {skill_type}。支持的类型: {', '.join(SKILL_TYPES.keys())}"]
        }

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
        "teacher_id": teacher_id,
        "skill_type": skill_type,
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


def search_skills(query: str, skill_type: Optional[str] = None, max_results: int = 10) -> List[Dict]:
    """
    智能搜索Skill（优化的关键词匹配）
    
    Args:
        query: 搜索查询
        skill_type: 可选的技能类型过滤
        max_results: 最大返回结果数
    
    Returns:
        List[Dict]: 匹配的Skill列表，按相关性排序
    """
    index = _load_skill_index()
    query_lower = query.lower()
    query_words = query_lower.split()  # 分词
    
    matched_skills = []

    for skill in index:
        # 技能类型过滤
        if skill_type and skill.get("技能类型") != skill_type:
            continue
        
        score = 0
        match_details = []

        # 1. 标题匹配（权重：10）
        title = skill.get("标题", "").lower()
        if query_lower in title:
            score += 10
            match_details.append(f"标题匹配: {skill.get('标题')}")
        
        # 2. 完整匹配标题中的所有词汇（权重：8）
        title_words = set(title.split())
        query_word_set = set(query_words)
        overlap = title_words & query_word_set
        if overlap:
            score += len(overlap) * 2
            match_details.append(f"标题词汇匹配: {', '.join(overlap)}")

        # 3. 技能描述匹配（权重：6）
        description = skill.get("技能描述", "").lower()
        if query_lower in description:
            score += 6
            match_details.append(f"描述匹配")
        
        # 4. 关键词精确匹配（权重：5）
        keywords = [kw.strip().lower() for kw in skill.get("关键词", "").split(",")]
        for kw in keywords:
            if query_lower == kw:  # 精确匹配
                score += 8
                match_details.append(f"关键词精确匹配: {kw}")
            elif query_lower in kw:  # 部分匹配
                score += 3
                match_details.append(f"关键词部分匹配: {kw}")
        
        # 5. 适用场景匹配（权重：4）
        scenario = skill.get("适用场景", "").lower()
        if query_lower in scenario:
            score += 4
            match_details.append(f"适用场景匹配")

        # 6. 技能类型相关关键词匹配（权重：2）
        skill_type_current = skill.get("技能类型", "")
        if skill_type_current in SKILL_TYPES:
            type_keywords = SKILL_TYPES[skill_type_current]["keywords"]
            for type_kw in type_keywords:
                if type_kw.lower() in query_lower:
                    score += 2
                    match_details.append(f"技能类型相关: {skill_type_current}")
                    break

        # 7. 计算相关性分数（考虑字段长度）
        # 避免短字段因偶然匹配获得高分
        if score > 0:
            text_length = len(title + description + skill.get("关键词", ""))
            normalized_score = score / (1 + text_length / 100)  # 归一化
            score = int(normalized_score * 10) / 10  # 保留一位小数

        if score > 0:
            skill_with_score = skill.copy()
            skill_with_score["_match_score"] = score
            skill_with_score["_match_details"] = match_details
            matched_skills.append(skill_with_score)

    # 按匹配分数排序，分数相同时按标题排序
    matched_skills.sort(key=lambda x: (-x["_match_score"], x.get("标题", "")))
    
    return matched_skills[:max_results]

def suggest_skills(skill_type: Optional[str] = None, limit: int = 5) -> List[Dict]:
    """
    推荐热门或高质量的Skill
    
    Args:
        skill_type: 可选的技能类型过滤
        limit: 推荐数量限制
    
    Returns:
        List[Dict]: 推荐的Skill列表
    """
    index = _load_skill_index()
    
    # 过滤技能类型
    if skill_type:
        skills = [s for s in index if s.get("技能类型") == skill_type]
    else:
        skills = index
    
    # 简单的推荐逻辑：基于关键词数量和描述完整性
    recommended = []
    for skill in skills:
        score = 0
        
        # 关键词数量
        keywords = skill.get("关键词", "").split(",")
        score += len([kw for kw in keywords if kw.strip()])
        
        # 描述完整性
        if skill.get("技能描述"):
            score += 2
        if skill.get("适用场景"):
            score += 2
            
        skill["_recommend_score"] = score
        recommended.append(skill)
    
    # 按推荐分数排序
    recommended.sort(key=lambda x: x["_recommend_score"], reverse=True)
    
    return recommended[:limit]


def fork_skill(original_title: str, new_title: str, teacher_id: str, modifications: Optional[str] = None) -> Dict:
    """
    复用(fork)现有Skill，支持版本追踪
    
    Args:
        original_title: 原Skill标题
        new_title: 新Skill标题  
        teacher_id: 教师ID
        modifications: 修改内容
    
    Returns:
        Dict: fork结果
    """
    # 验证教师身份
    teacher_id = get_current_teacher_id(teacher_id)
    
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

    # 添加fork信息和版本追踪
    fork_info = f"\n> **Fork自**: {original_title} by {teacher_id} on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    fork_info += f"> **原Skill创建时间**: {_extract_original_create_time(content)}\n"
    fork_info += f"> **版本**: 1.0 (forked)\n"
    
    content = content.replace("## 技能描述", fork_info + "\n## 技能描述")

    # 应用修改
    if modifications:
        content += f"\n\n## 定制修改\n{modifications}\n"
        content += f"\n> **修改时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"

    # 保存为新Skill
    result = create_skill(new_title, content, teacher_id)
    
    # 记录fork关系
    if result["success"]:
        _record_fork_relationship(original_title, new_title, teacher_id)
    
    return result

def _extract_original_create_time(content: str) -> str:
    """从原Skill内容中提取创建时间"""
    meta_match = re.search(r"- 创建时间：([^\n]+)", content)
    if meta_match:
        return meta_match.group(1).strip()
    return "未知"

def _record_fork_relationship(original_title: str, new_title: str, teacher_id: str):
    """记录fork关系，用于版本追踪"""
    fork_history_path = os.path.join(DATA_DIR, "fork_history.json")
    
    fork_history = []
    if os.path.exists(fork_history_path):
        with open(fork_history_path, "r", encoding="utf-8") as f:
            fork_history = json.load(f)
    
    fork_record = {
        "original_title": original_title,
        "new_title": new_title,
        "fork_by": teacher_id,
        "fork_time": datetime.now().isoformat(),
        "id": f"fork_{len(fork_history) + 1}"
    }
    
    fork_history.append(fork_record)
    
    with open(fork_history_path, "w", encoding="utf-8") as f:
        json.dump(fork_history, f, ensure_ascii=False, indent=2)

def get_fork_history(skill_title: str) -> List[Dict]:
    """获取Skill的fork历史"""
    fork_history_path = os.path.join(DATA_DIR, "fork_history.json")
    
    if not os.path.exists(fork_history_path):
        return []
    
    with open(fork_history_path, "r", encoding="utf-8") as f:
        fork_history = json.load(f)
    
    # 查找该skill的所有fork记录（作为原始skill和作为fork后的skill）
    related_forks = []
    for record in fork_history:
        if record["original_title"] == skill_title or record["new_title"] == skill_title:
            related_forks.append(record)
    
    return related_forks


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

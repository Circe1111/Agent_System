import os
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse, JSONResponse
from utils.response import success, fail

router = APIRouter(prefix="/resources", tags=["资源"])

# 知识库根目录
DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data"))
KB_DIR = os.path.join(DATA_DIR, "知识库数据")

# 课程元数据（与知识库目录对应）
COURSE_META = {
    "Python": {
        "id": 1,
        "title": "Python程序设计",
        "description": "从零基础到进阶，系统学习Python编程语言，涵盖基础语法、数据结构、面向对象编程与实战案例。",
        "category": "编程",
        "level": "初级",
        "bilibili_url": "https://www.bilibili.com/video/BV1qW4y1a7fU",
        "bilibili_title": "黑马程序员Python教程_8天Python从入门到精通",
    },
    "计算机网络": {
        "id": 2,
        "title": "计算机网络",
        "description": "深入理解网络协议、TCP/IP体系结构、局域网技术、网络层与传输层核心原理。",
        "category": "基础课",
        "level": "中级",
        "bilibili_url": "https://www.bilibili.com/video/BV1c4411d7jb",
        "bilibili_title": "湖科大教书匠_计算机网络微课堂",
    },
    "编译原理": {
        "id": 3,
        "title": "编译原理",
        "description": "系统学习词法分析、语法分析、语义分析、中间代码生成与目标代码优化等编译核心理论。",
        "category": "专业课",
        "level": "高级",
        "bilibili_url": "https://www.bilibili.com/video/BV1cJ411u713",
        "bilibili_title": "哈工大_编译原理（全）",
    },
    "人工神经网络": {
        "id": 4,
        "title": "人工神经网络",
        "description": "基于神经网络的理论基础、训练方法与实践案例，涵盖CNN、Transformer等前沿模型。",
        "category": "人工智能",
        "level": "中级",
        "bilibili_url": "https://www.bilibili.com/video/BV1Xe4y1S7i8",
        "bilibili_title": "五大深度神经网络教程_CNN/RNN/GAN/Transformer",
    },
    "Linux": {
        "id": 5,
        "title": "Linux操作系统",
        "description": "从Linux概述到Shell编程，系统学习Linux基础命令、文件操作、进程管理与服务器配置。",
        "category": "基础课",
        "level": "初级",
        "bilibili_url": "https://www.bilibili.com/video/BV13AjPzREqR",
        "bilibili_title": "2025版B站最全Linux操作系统快速入门",
    },
}

FILE_TYPE_MAP = {
    ".pdf": "pdf",
    ".docx": "doc",
    ".doc": "doc",
    ".pptx": "ppt",
    ".ppt": "ppt",
    ".txt": "text",
    ".md": "text",
    ".json": "text",
    ".csv": "text",
}

TYPE_LABEL_MAP = {
    "pdf": "PDF文档",
    "doc": "Word文档",
    "ppt": "PPT演示文稿",
    "text": "文本文件",
}

def _get_file_type(filename: str) -> str:
    _, ext = os.path.splitext(filename)
    return FILE_TYPE_MAP.get(ext.lower(), "file")

def _get_type_label(file_type: str) -> str:
    return TYPE_LABEL_MAP.get(file_type, "文件")

def _scan_course_files(course_name: str) -> list:
    """扫描指定课程目录下的所有文件"""
    course_dir = os.path.join(KB_DIR, course_name)
    if not os.path.isdir(course_dir):
        return []

    files = []
    for root, dirs, filenames in os.walk(course_dir):
        for filename in filenames:
            file_path = os.path.join(root, filename)
            relative_path = os.path.relpath(file_path, course_dir)
            file_type = _get_file_type(filename)
            file_size = os.path.getsize(file_path)
            files.append({
                "id": abs(hash(file_path)) % 100000,
                "title": filename,
                "relative_path": relative_path,
                "absolute_path": file_path,
                "file_type": file_type,
                "type_label": _get_type_label(file_type),
                "size": file_size,
                "size_display": _format_size(file_size),
                "category": os.path.dirname(relative_path).replace("\\", "/") if os.path.dirname(relative_path) else "根目录",
            })
    # 按文件名排序
    files.sort(key=lambda f: f["title"])
    return files

def _build_file_tree(course_name: str) -> list:
    """将课程文件组织为树形分组结构"""
    files = _scan_course_files(course_name)
    
    groups = {}  # key: top-level group name
    
    for f in files:
        category = f.get("category", "根目录")
        # 取第一级分组名
        parts = category.split("/")
        top_group = parts[0] if parts[0] else "根目录"
        sub_group = "/".join(parts[1:]) if len(parts) > 1 else ""
        
        if top_group not in groups:
            groups[top_group] = {"subgroups": {}, "files": []}
        
        if sub_group:
            if sub_group not in groups[top_group]["subgroups"]:
                groups[top_group]["subgroups"][sub_group] = []
            groups[top_group]["subgroups"][sub_group].append(f)
        else:
            groups[top_group]["files"].append(f)
    
    # 构建排序后的树形结构
    result = []
    for group_name in sorted(groups.keys()):
        group = groups[group_name]
        children = []
        
        # 子分组
        for sub_name in sorted(group["subgroups"].keys()):
            sub_files = sorted(group["subgroups"][sub_name], key=lambda f: f["title"])
            children.append({
                "name": sub_name,
                "type": "subgroup",
                "files": sub_files,
                "file_count": len(sub_files),
            })
        
        # 直接文件
        direct_files = sorted(group["files"], key=lambda f: f["title"])
        if direct_files:
            children.append({
                "name": "",
                "type": "files",
                "files": direct_files,
                "file_count": len(direct_files),
            })
        
        result.append({
            "name": group_name,
            "children": children,
            "file_count": sum(c["file_count"] for c in children),
        })
    
    return result

def _format_size(size: int) -> str:
    if size < 1024:
        return f"{size} B"
    elif size < 1024 * 1024:
        return f"{size / 1024:.1f} KB"
    else:
        return f"{size / (1024 * 1024):.1f} MB"

@router.get("/courses")
def list_courses():
    """获取所有课程列表（从知识库目录扫描）"""
    courses = []
    if not os.path.isdir(KB_DIR):
        return success(data={"courses": courses})

    for dir_name in sorted(os.listdir(KB_DIR)):
        dir_path = os.path.join(KB_DIR, dir_name)
        if os.path.isdir(dir_path):
            meta = COURSE_META.get(dir_name, {
                "id": abs(hash(dir_name)) % 100,
                "title": dir_name,
                "description": "",
                "category": "未分类",
                "level": "初级",
            })
            files = _scan_course_files(dir_name)
            courses.append({
                **meta,
                "dir_name": dir_name,
                "resource_count": len(files),
            })

    courses.sort(key=lambda c: c["id"])
    return success(data={"courses": courses})

@router.get("/courses/{course_name}/files")
def list_course_files(course_name: str):
    """获取指定课程的文件列表（树形分组结构）"""
    if not os.path.isdir(os.path.join(KB_DIR, course_name)):
        return fail(msg=f"课程 '{course_name}' 不存在", code=404)

    tree = _build_file_tree(course_name)
    total = sum(g["file_count"] for g in tree)
    return success(data={"groups": tree, "total": total})

@router.get("/download")
def download_file(path: str = Query(..., description="文件在知识库中的相对路径"),
                   course: str = Query(..., description="课程名称")):
    """下载知识库中的文件"""
    safe_path = os.path.normpath(path)
    if safe_path.startswith("..") or os.path.isabs(safe_path):
        raise HTTPException(status_code=400, detail="非法的文件路径")

    file_path = os.path.join(KB_DIR, course, safe_path)
    if not os.path.isfile(file_path):
        raise HTTPException(status_code=404, detail="文件不存在")

    # 确保文件在知识库目录内
    if not os.path.abspath(file_path).startswith(os.path.abspath(KB_DIR)):
        raise HTTPException(status_code=400, detail="非法的文件路径")

    filename = os.path.basename(file_path)
    return FileResponse(
        path=file_path,
        filename=filename,
        media_type="application/octet-stream",
        headers={"Content-Disposition": f'attachment; filename="{filename.encode("utf-8", "surrogateescape").decode("latin-1")}"'}
    )

@router.get("/preview")
def preview_file(path: str = Query(..., description="文件在知识库中的相对路径"),
                  course: str = Query(..., description="课程名称")):
    """预览文本文件内容（支持 .txt, .md, .json, .csv）"""
    safe_path = os.path.normpath(path)
    if safe_path.startswith("..") or os.path.isabs(safe_path):
        return fail(msg="非法的文件路径")

    file_path = os.path.join(KB_DIR, course, safe_path)
    if not os.path.isfile(file_path):
        return fail(msg="文件不存在", code=404)

    if not os.path.abspath(file_path).startswith(os.path.abspath(KB_DIR)):
        return fail(msg="非法的文件路径")

    _, ext = os.path.splitext(safe_path)
    ext = ext.lower()

    if ext not in [".txt", ".md", ".json", ".csv", ".py", ".html", ".css", ".js", ".xml", ".yaml", ".yml"]:
        return fail(msg=f"不支持预览 {ext} 格式的文件，请下载后查看", code=400)

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        return success(data={
            "content": content,
            "filename": os.path.basename(file_path),
            "file_type": _get_file_type(safe_path),
            "size": len(content),
        })
    except UnicodeDecodeError:
        return fail(msg="无法以文本方式读取该文件，可能是二进制文件", code=400)
    except Exception as e:
        return fail(msg=f"读取文件失败: {str(e)}", code=500)
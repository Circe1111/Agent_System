import os
import json
from dotenv import load_dotenv

# Internal project imports (RAG + DB + prompts)
from rag.document_loader import DocumentLoader, TextSplitter, Document
from rag.embeddings import EmbeddingClient
from rag.vector_store import VectorStore, RAGRetriever
from database.connect import get_db
from database.models import Students, LearningRecords, EduUser
from prompt.manager import prompt_manager

# Unified LLM client (OpenAI-compatible)
from services.llm_client import LLMClient

load_dotenv()

_retriever = None


def get_retriever():
    global _retriever
    if _retriever is not None:
        return _retriever

    vector_store = VectorStore()

    if not vector_store.load():
        print(">>> 未找到FAISS索引，开始构建...")
        loader = DocumentLoader()
        splitter = TextSplitter(chunk_size=500, chunk_overlap=50)

        embedding = EmbeddingClient(model_type="local")
        if embedding.model_type == "simple":
            print(">>> 使用简单向量模式（text2vec模型未加载）")

        docs = loader.load_directory()
        if not docs:
            default_doc = Document(
                content="""Python是一种高级编程语言，以其简洁优雅的语法和强大的功能而闻名。
Python支持多种编程范式，包括面向对象、函数式和过程式编程。
Python的核心特性包括：动态类型、自动内存管理、丰富的标准库。
常用的Python数据结构包括：列表(list)、元组(tuple)、字典(dict)、集合(set)。
Python的控制流语句包括：if-else、for循环、while循环、break、continue。
函数是Python的基本构建块，可以使用def关键字定义。
面向对象编程是Python的核心特性之一，支持类、继承、多态等概念。
文件操作是Python的重要功能，可以读取、写入和处理各种文件格式。
异常处理使用try-except语句，可以捕获和处理程序运行时的错误。
Python有丰富的第三方库，如numpy、pandas、matplotlib、scikit-learn等。""",
                metadata={"file_name": "default_python.txt"}
            )
            docs = [default_doc]

        chunks = splitter.split_documents(docs)
        if chunks:
            texts = [chunk.content for chunk in chunks]
            embeddings = embedding.embed(texts)
            vector_store.add_documents(chunks, embeddings)
            vector_store.save()
            print(f">>> FAISS索引构建完成，共 {len(chunks)} 个文档块")
        else:
            print(">>> 无文档可索引")

    _retriever = RAGRetriever(vector_store)
    return _retriever


def call_llm(messages, temperature=0.7, max_tokens=800, max_retries=3):
    """Unified LLM call via LLMClient. Returns the assistant text or None."""
    client = LLMClient()
    last_err: Exception | None = None
    for attempt in range(max_retries):
        try:
            return client.chat_text(
                messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
        except Exception as exc:  # noqa: BLE001
            last_err = exc
            print(f">>> LLM 请求失败 (第 {attempt + 1}/{max_retries} 次): {exc}")
            if attempt < max_retries - 1:
                import time
                time.sleep(2)
    print(f">>> LLM 彻底失败: {last_err}")
    return None


def get_user_profile(user_id: str):
    db = next(get_db())
    try:
        user_profile = db.query(Students).filter(Students.id == user_id).first()
        edu_user = db.query(EduUser).filter(EduUser.id == user_id).first()
        if user_profile or edu_user:
            profile = {}
            if edu_user:
                profile["姓名"] = edu_user.username or edu_user.nickname or ""
                profile["账号"] = edu_user.username or ""
            if user_profile:
                if user_profile.name:
                    profile["姓名"] = user_profile.name
                if user_profile.major:
                    profile["专业"] = user_profile.major
                if user_profile.knowledge_level:
                    profile["知识基础"] = user_profile.knowledge_level
                if user_profile.learning_preference:
                    profile["学习偏好"] = user_profile.learning_preference
                if user_profile.weak_knowledge:
                    profile["薄弱知识"] = user_profile.weak_knowledge
                if user_profile.study_goal:
                    profile["学习目标"] = user_profile.study_goal
                if user_profile.study_time:
                    profile["学习时间"] = user_profile.study_time
                if user_profile.course:
                    profile["课程"] = user_profile.course
                if user_profile.raw_json:
                    try:
                        if isinstance(user_profile.raw_json, dict):
                            profile.update(user_profile.raw_json)
                    except Exception:
                        pass
            return profile
    except Exception as e:
        print(f">>> 获取用户画像失败: {e}")
    finally:
        db.close()
    return {}


def get_user_learning_records(user_id: str):
    db = next(get_db())
    try:
        records = db.query(LearningRecords).filter(LearningRecords.user_id == user_id).all()
        result = []
        for r in records:
            result.append({
                "chapter": r.chapter,
                "score": r.score,
                "correct_rate": float(r.correct_rate) if r.correct_rate else 0,
                "problems_done": r.problems_done,
                "duration_minutes": r.duration_minutes,
                "date": str(r.study_date)
            })
        return result
    except Exception as e:
        print(f">>> 获取学习记录失败: {e}")
    finally:
        db.close()
    return []


# ----- 1. 画像机器人 -----
def profile_agent(state: dict):
    print(">>> 1. 画像机器人：正在分析你的学习特征...")
    user_id = state.get("user_id", "")
    messages = state.get("messages", [])
    last_msg = messages[-1].get("content", "") if messages and isinstance(messages[-1], dict) else (messages[-1].content if messages else "无")

    db_profile = get_user_profile(user_id)

    if db_profile:
        print(f">>> 从数据库获取用户画像: {db_profile.get('姓名', '')}, 薄弱知识: {db_profile.get('薄弱知识', '')}")
        profile = {
            "knowledge_base": db_profile.get("知识基础", "中等"),
            "cognitive_style": db_profile.get("学习偏好", "视觉型"),
            "weak_points": db_profile.get("薄弱知识", ""),
            "interest": db_profile.get("课程", "Python程序设计"),
            "learning_pace": "中等",
            "emotional_state": "积极",
            "name": db_profile.get("姓名", ""),
            "major": db_profile.get("专业", ""),
            "goal": db_profile.get("学习目标", ""),
            "time": db_profile.get("学习时间", "")
        }
    else:
        prompt = f"""你是一个教育心理学专家。根据学生的发言："{last_msg}"。
输出一份严格的JSON格式学生画像（不要带任何其他废话，只输出JSON）。
维度包括：knowledge_base, cognitive_style, weak_points, interest, learning_pace, emotional_state。"""

        response = call_llm([{"role": "user", "content": prompt}])

        try:
            profile = json.loads(response) if response else None
        except Exception:
            profile = None

        if not profile:
            profile = {
                "knowledge_base": "初学者",
                "cognitive_style": "视觉型",
                "weak_points": "数学推导",
                "interest": "AI",
                "learning_pace": "中等",
                "emotional_state": "积极",
                "name": "学生",
                "major": "",
                "goal": "",
                "time": ""
            }
    return {"profile": profile}


# ----- 2. RAG检索机器人 -----
def rag_agent(state: dict):
    print(">>> 2. RAG机器人：正在检索知识库...")
    messages = state.get("messages", [])
    last_msg = messages[-1].get("content", "") if messages and isinstance(messages[-1], dict) else (messages[-1].content if messages else "")

    retriever = get_retriever()
    embedding = EmbeddingClient(model_type="local")

    retrieved_docs = retriever.retrieve(last_msg, embedding, top_k=5)

    if not retrieved_docs:
        print(">>> RAG检索无结果，使用默认知识")
        retrieved_docs = [{"content": "Python是一种高级编程语言，支持多种编程范式，包括面向对象、函数式和过程式编程。", "source": "默认知识库"}]

    print(f">>> RAG检索完成，找到 {len(retrieved_docs)} 条相关文档")
    return {"retrieved_docs": retrieved_docs}


# ----- 3. 资源生成机器人 -----
def generator_agent(state: dict):
    print(">>> 3. 生成机器人：正在为你制作学习资料...")
    profile = state.get("profile", {})
    docs = state.get("retrieved_docs", [])

    combined_docs = ""
    doc_sources = []
    for doc in docs:
        if isinstance(doc, dict):
            combined_docs += doc.get("content", "") + "\n\n"
            doc_sources.append(doc.get("source", "未知"))
        else:
            combined_docs += str(doc) + "\n\n"

    if not combined_docs.strip():
        combined_docs = "Python是一种高级编程语言，支持多种编程范式。"

    topic = profile.get("weak_points", "") or "Python基础"

    prompt_text = prompt_manager.render_prompt("P001", topic=topic)
    if prompt_text is None:
        prompt_text = f"""你是一位Python程序设计课程的资深教师。请根据主题「{topic}」生成一份适合大学生学习的讲义。
要求：1) 内容由浅入深 2) 包含代码示例 3) 包含常见错误说明 4) 包含课后思考题。
请严格控制输出长度，总字数不超过600字，用极简风格回答。
参考知识：{combined_docs[:500]}"""

    content = call_llm([{"role": "user", "content": prompt_text}])

    if content is None:
        content = f"""
1. **知识讲解文档**：{topic}是Python中的重要知识点。

2. **随堂测验**：
   - 题目1：关于{topic}的基础问题？
   - 题目2：{topic}的进阶应用？

3. **思维导图大纲**：- {topic} - 基础概念 - 应用场景 - 实战练习"""

    exercises_prompt = prompt_manager.render_prompt("P002", topic=topic, count=2, difficulty="中等")
    exercises = ""
    if exercises_prompt:
        exercises = call_llm([{"role": "user", "content": exercises_prompt}])

    full_content = content
    if exercises:
        full_content += "\n\n## 练习题\n" + exercises

    return {"generated_resource": {"type": "multi_resource", "content": full_content}}


# ----- 4. 审核机器人 -----
def guardrail_agent(state: dict):
    print(">>> 4. 审核机器人：正在检查内容质量...")
    content = state.get("generated_resource", {}).get("content", "")
    retry_count = state.get("retry_count", 0)

    keywords = ["Python", "代码", "函数", "变量", "循环", "条件", "面向对象", "模块", "文件"]
    has_knowledge = any(k in content for k in keywords)

    if has_knowledge and len(content) > 50:
        return {"is_approved": True, "retry_count": retry_count}
    else:
        print(">>> 警告：内容质量不足，已拦截！")
        return {"is_approved": False, "retry_count": retry_count + 1}


# ----- 5. 路径规划机器人 -----
def planner_agent(state: dict):
    print(">>> 5. 规划机器人：正在制定专属学习路线...")
    profile = state.get("profile", {})
    resource = state.get("generated_resource", {}).get("content", "")

    user_id = state.get("user_id", "")
    learning_records = get_user_learning_records(user_id)

    records_summary = ""
    if learning_records:
        recent_records = learning_records[-5:]
        records_summary = "\n".join([f"{r['chapter']}: 得分{r['score']}, 正确率{r['correct_rate']}" for r in recent_records])

    weak_points = profile.get("weak_points", "")

    prompt_text = prompt_manager.render_prompt(
        "P012",
        target_audience=profile.get("name", "学生"),
        start_level=profile.get("knowledge_base", "中等"),
        target_level="熟练掌握",
        available_time=profile.get("time", "每天2小时")
    )

    if prompt_text is None:
        prompt_text = f"""你是学业规划师。学生画像：{profile}。
薄弱知识：{weak_points}
请规划3个连续的学习步骤（只输出JSON数组格式，不要任何其他文字）：
[{{"step_name": "步骤名", "action": "具体行动", "time_minutes": 分钟数}}]"""

    response = call_llm([{"role": "user", "content": prompt_text}])

    try:
        path = json.loads(response) if response else None
    except Exception:
        path = None

    if not path:
        path = [
            {"step_name": "理论学习", "action": "阅读讲解文档", "time_minutes": 20},
            {"step_name": "巩固练习", "action": "完成练习题", "time_minutes": 15},
            {"step_name": "知识总结", "action": "整理笔记和思维导图", "time_minutes": 10}
        ]
    return {"learning_path": path}
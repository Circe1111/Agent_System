from sqlalchemy.orm import Session
from database.models import Students, EduUser
import json

FIELD_MAP = {
    # 后端 snake_case 键
    "knowledge_base": "knowledge_level",
    "cognitive_style": "learning_preference",
    "weak_points": "weak_knowledge",
    "interest": "course",
    "name": "name",
    "major": "major",
    "goal": "study_goal",
    "time": "study_time",
    "learning_style": "learning_style",
    # 前端 camelCase 键（兼容）
    "knowledgeBase": "knowledge_level",
    "cognitiveStyle": "learning_preference",
    "weakPoints": "weak_knowledge",
    "interest": "course",
    "learningGoals": "study_goal",
    "preferredLearningStyle": "learning_style",
    "errorPreferences": "weak_knowledge",
    "currentProgress": "knowledge_level",
}


def get_user_profile(db: Session, user_id: int):
    return db.query(Students).filter(Students.id == user_id).first()


def _merge_csv(existing: str, new_val) -> str:
    existing_set = set()
    if existing:
        existing_set = {s.strip() for s in existing.split(",") if s.strip()}

    if isinstance(new_val, list):
        new_set = {str(v).strip() for v in new_val if str(v).strip()}
    elif isinstance(new_val, str):
        new_set = {s.strip() for s in new_val.split(",") if s.strip()}
    else:
        new_set = set()

    merged = existing_set | new_set
    return ",".join(sorted(merged))


def _update_weak_point_counts(existing_raw_json: dict, new_weak_points) -> dict:
    counts = {}
    if existing_raw_json and isinstance(existing_raw_json, dict):
        counts = existing_raw_json.get("weak_point_counts", {})
        if not isinstance(counts, dict):
            counts = {}

    if isinstance(new_weak_points, list):
        items = [str(v).strip() for v in new_weak_points if str(v).strip()]
    elif isinstance(new_weak_points, str):
        items = [s.strip() for s in new_weak_points.split(",") if s.strip()]
    else:
        items = []

    for item in items:
        counts[item] = counts.get(item, 0) + 1

    return counts


def update_user_profile(db: Session, user_id: int, portrait_data: dict):
    profile = db.query(Students).filter(Students.id == user_id).first()

    if not profile:
        edu_user = db.query(EduUser).filter(EduUser.id == user_id).first()
        name = edu_user.username if edu_user else f"用户{user_id}"
        major = edu_user.major if edu_user else ""
        profile = Students(id=user_id, name=name, major=major)
        db.add(profile)
        db.flush()

    for src_key, model_field in FIELD_MAP.items():
        if src_key in portrait_data:
            val = portrait_data[src_key]
            if model_field == "weak_knowledge":
                existing = getattr(profile, model_field, "") or ""
                val = _merge_csv(existing, val)
            elif model_field == "course":
                existing = getattr(profile, model_field, "") or ""
                val = _merge_csv(existing, val)
            elif model_field == "knowledge_level" and isinstance(val, (int, float)):
                val = str(val)
            setattr(profile, model_field, val)

    existing_raw = profile.raw_json or {}
    if not isinstance(existing_raw, dict):
        existing_raw = {}
    new_weak_points = portrait_data.get("weak_points") or portrait_data.get("weakPoints") or []
    existing_raw["weak_point_counts"] = _update_weak_point_counts(existing_raw, new_weak_points)
    if "vark_scores" in portrait_data:
        from datetime import datetime
        vark_entry = {
            "V": portrait_data["vark_scores"].get("V", 0.25),
            "A": portrait_data["vark_scores"].get("A", 0.25),
            "R": portrait_data["vark_scores"].get("R", 0.25),
            "K": portrait_data["vark_scores"].get("K", 0.25),
            "trigger_words": portrait_data["vark_scores"].get("trigger_words", []),
            "reason": portrait_data["vark_scores"].get("reason", ""),
            "timestamp": datetime.utcnow().isoformat(),
        }
        vark_history = existing_raw.get("vark_history", [])
        if not isinstance(vark_history, list):
            vark_history = []
        vark_history.append(vark_entry)
        existing_raw["vark_history"] = vark_history
        existing_raw["vark_scores"] = vark_entry
    if "style_analysis" in portrait_data:
        from datetime import datetime
        sa = portrait_data["style_analysis"]
        if isinstance(sa, dict):
            sa["timestamp"] = datetime.utcnow().isoformat()
            existing_raw["style_analysis"] = sa
    profile.raw_json = existing_raw
    db.commit()
    db.refresh(profile)
    return profile


def get_full_profile(db: Session, user_id: int) -> dict:
    profile = db.query(Students).filter(Students.id == user_id).first()
    edu_user = db.query(EduUser).filter(EduUser.id == user_id).first()

    if not profile:
        return {
            "user_id": user_id,
            "username": edu_user.username if edu_user else "",
            "nickname": edu_user.nickname if edu_user else "",
            "name": "",
            "major": edu_user.major if edu_user else "",
            "knowledge_level": "",
            "learning_preference": "",
            "learning_style": "",
            "weak_knowledge": "",
            "study_goal": "",
            "study_time": "",
            "course": "",
            "raw_json": {},
        }

    return {
        "user_id": user_id,
        "username": edu_user.username if edu_user else "",
        "nickname": edu_user.nickname if edu_user else "",
        "name": profile.name or "",
        "major": profile.major or "",
        "knowledge_level": profile.knowledge_level or "",
        "learning_preference": profile.learning_preference or "",
        "learning_style": profile.learning_style or "",
        "weak_knowledge": profile.weak_knowledge or "",
        "study_goal": profile.study_goal or "",
        "study_time": profile.study_time or "",
        "course": profile.course or "",
        "raw_json": profile.raw_json or {},
    }
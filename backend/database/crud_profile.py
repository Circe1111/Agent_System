from sqlalchemy.orm import Session
from database.models import Students
import json

FIELD_MAP = {
    "knowledge_base": "knowledge_level",
    "cognitive_style": "learning_preference",
    "weak_points": "weak_knowledge",
    "interest": "course",
    "name": "name",
    "major": "major",
    "goal": "study_goal",
    "time": "study_time",
}


def get_user_profile(db: Session, user_id: int):
    return db.query(Students).filter(Students.id == user_id).first()


def update_user_profile(db: Session, user_id: int, portrait_data: dict):
    profile = get_user_profile(db, user_id)
    if not profile:
        profile = Students(id=user_id)
        db.add(profile)

    for src_key, model_field in FIELD_MAP.items():
        if src_key in portrait_data:
            setattr(profile, model_field, portrait_data[src_key])

    profile.raw_json = portrait_data

    db.commit()
    db.refresh(profile)
    return profile

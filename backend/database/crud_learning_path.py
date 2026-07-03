from sqlalchemy.orm import Session
from database.models import LearningPath


def save_learning_path(db: Session, user_id: int, goal: str, steps: list) -> LearningPath:
    existing = db.query(LearningPath).filter(
        LearningPath.user_id == user_id,
        LearningPath.goal == goal
    ).first()

    if existing:
        existing.steps = steps
        db.commit()
        db.refresh(existing)
        return existing

    path = LearningPath(user_id=user_id, goal=goal, steps=steps)
    db.add(path)
    db.commit()
    db.refresh(path)
    return path


def get_learning_path(db: Session, user_id: int, goal: str = None):
    if goal:
        return db.query(LearningPath).filter(
            LearningPath.user_id == user_id,
            LearningPath.goal == goal
        ).first()
    return db.query(LearningPath).filter(
        LearningPath.user_id == user_id
    ).order_by(LearningPath.updated_at.desc()).all()


def get_user_learning_paths(db: Session, user_id: int):
    return db.query(LearningPath).filter(
        LearningPath.user_id == user_id
    ).order_by(LearningPath.updated_at.desc()).all()


def delete_learning_path(db: Session, user_id: int, goal: str = None):
    if goal:
        db.query(LearningPath).filter(
            LearningPath.user_id == user_id,
            LearningPath.goal == goal
        ).delete()
    else:
        db.query(LearningPath).filter(
            LearningPath.user_id == user_id
        ).delete()
    db.commit()
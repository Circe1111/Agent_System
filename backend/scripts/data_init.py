import os
import json
from datetime import datetime, date
from sqlalchemy.orm import Session
from app.database import engine, Base, EduUser, EduProfile, LearningRecord, SessionLocal


def load_student_data():
    data_path = os.path.join("data", "学生画像数据", "student_data.json")
    if os.path.exists(data_path):
        with open(data_path, "r", encoding="utf-8") as f:
            content = f.read()
            if content.startswith("/*"):
                end_comment = content.find("*/")
                if end_comment != -1:
                    content = content[end_comment + 2:]
            content = content.strip()
            return json.loads(content)
    return []


def load_learning_records():
    data_path = os.path.join("data", "学习记录", "learning_records.json")
    if os.path.exists(data_path):
        with open(data_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def init_student_data(db: Session):
    students = load_student_data()
    print(f">>> 加载学生数据: {len(students)} 条")

    for i, student in enumerate(students):
        username = f"user{i+1:04d}"
        password = "123456"
        nickname = student.get("姓名", f"学生{i+1}")
        major = student.get("专业", "")

        existing_user = db.query(EduUser).filter(EduUser.username == username).first()
        if existing_user:
            continue

        user = EduUser(
            username=username,
            password=password,
            nickname=nickname,
            major=major
        )
        db.add(user)

        profile_json = json.dumps({
            "姓名": student.get("姓名", ""),
            "年龄": student.get("年龄", 0),
            "专业": student.get("专业", ""),
            "课程": student.get("课程", ""),
            "学习目标": student.get("学习目标", ""),
            "知识基础": student.get("知识基础", ""),
            "学习偏好": student.get("学习偏好", ""),
            "薄弱知识": student.get("薄弱知识", ""),
            "学习时间": student.get("学习时间", "")
        }, ensure_ascii=False)

        profile = EduProfile(
            user_id=i+1,
            weak_points=student.get("薄弱知识", ""),
            learning_json=profile_json
        )
        db.add(profile)

    db.commit()
    print(f">>> 学生数据导入完成")


def init_learning_records(db: Session):
    records = load_learning_records()
    print(f">>> 加载学习记录: {len(records)} 条")

    seen_ids = set()
    unique_records = []
    for record in records:
        if record["id"] not in seen_ids:
            seen_ids.add(record["id"])
            unique_records.append(record)
        else:
            print(f">>> 跳过重复记录: {record['id']}")
    
    print(f">>> 去重后记录数: {len(unique_records)}")

    for record in unique_records:
        existing = db.query(LearningRecord).filter(LearningRecord.id == record["id"]).first()
        if existing:
            continue

        try:
            record_date = datetime.strptime(record["date"], "%Y-%m-%d").date()
        except:
            record_date = date.today()

        learning_record = LearningRecord(
            id=record["id"],
            user_id=record["user_id"],
            course=record.get("course", ""),
            chapter=record.get("chapter", ""),
            score=record.get("score", 0),
            correct_rate=record.get("correct_rate", 0),
            problems_done=record.get("problems_done", 0),
            duration_minutes=record.get("duration_minutes", 0),
            date=record_date,
            time_slot=record.get("time_slot", "")
        )
        db.add(learning_record)

    db.commit()
    print(f">>> 学习记录导入完成")


def main():
    print(">>> 初始化数据库...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    print(">>> 数据库表创建完成")

    db = SessionLocal()
    try:
        init_student_data(db)
        init_learning_records(db)
        print(">>> 所有数据初始化完成！")
    finally:
        db.close()


if __name__ == "__main__":
    main()
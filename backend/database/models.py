from sqlalchemy import Column, Integer, String, Text, DateTime, Numeric, Date, JSON, func
from sqlalchemy.sql import func
from .connect import Base


# 用户表
class EduUser(Base):
    __tablename__ = "edu_user"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(100), nullable=False)
    nickname = Column(String(50))
    major = Column(String(50))
    create_time = Column(DateTime, default=func.now())

# 对话记录表
class EduChat(Base):
    __tablename__ = "edu_chat"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer)
    session_id = Column(String(100))
    content = Column(Text)
    role = Column(String(20))
    create_time = Column(DateTime, default=func.now())


# 学生画像表 students（替代原edu_profile）
class Students(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键ID")
    name = Column(String(50), nullable=False, comment="姓名")
    age = Column(Integer, comment="年龄")
    major = Column(String(100), comment="专业")
    course = Column(String(100), comment="课程")
    study_goal = Column(String(255), comment="学习目标")
    knowledge_level = Column(String(50), comment="知识基础")
    learning_preference = Column(String(50), comment="学习偏好")
    weak_knowledge = Column(String(255), comment="薄弱知识")
    study_time = Column(String(50), comment="学习时间")
    raw_json = Column(JSON, comment="原始JSON数据（可选）")
    created_at = Column(DateTime, default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), comment="更新时间")


# 学习记录表 learning_records
class LearningRecords(Base):
    __tablename__ = "learning_records"

    id = Column(String(64), primary_key=True, comment="记录id，如 RU0001_000")
    user_id = Column(String(50), comment="用户 id，如 U0001")
    course = Column(String(200), comment="课程")
    chapter = Column(String(200), comment="章节")
    score = Column(Integer, comment="得分")
    correct_rate = Column(Numeric(5, 4), comment="正确率（0-1）")
    problems_done = Column(Integer, comment="完成题目数")
    duration_minutes = Column(Integer, comment="持续分钟数")
    study_date = Column(Date, comment="学习日期")
    time_slot = Column(String(20), comment="时间段，如 10:00-12:00")
    raw_json = Column(JSON, comment="原始 JSON 数据（可选）")
    created_at = Column(DateTime, default=func.now(), comment="创建时间")

# 资源存储表
class EduResource(Base):
    __tablename__ = "edu_resource"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer)
    resource_type = Column(String(30))
    content = Column(Text)
    progress = Column(Integer, default=0)
    create_time = Column(DateTime, default=func.now())
from sqlalchemy import Column, Integer, String, Text, ForeignKey, JSON, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
# 使用统一的 Base 注册（来自 database.connect）
from database.connect import Base

class Conversation(Base):
    __tablename__ = "conversation"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True, comment="对话主键")
    # 临时注释外键
    # user_id = Column(Integer, ForeignKey("edu_user.id"), nullable=False, comment="关联用户")
    user_id = Column(Integer, nullable=False, comment="关联用户")
    session_id = Column(String(128), nullable=False, comment="会话唯一标识")
    role = Column(String(32), nullable=False, comment="user/assistant")
    content = Column(Text, nullable=False, comment="对话内容")
    portrait_json = Column(JSON, nullable=True, comment="画像快照")
    create_time = Column(DateTime, server_default=func.now())
    # 临时注释关联
    # user = relationship("User")
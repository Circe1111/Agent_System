import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


def ensure_default_user():
    from database.models import EduUser, Students, LearningRecords, EduChat, EduResource, Conversation
    from database import crud

    db = SessionLocal()
    try:
        # 确保 students 表有 learning_style 列（兼容旧数据库）
        try:
            db.execute(text("ALTER TABLE students ADD COLUMN learning_style VARCHAR(50)"))
            db.commit()
        except Exception:
            db.rollback()
        
        existing = crud.get_user_by_username(db, "admin")
        if not existing:
            crud.create_user(db, {"username": "admin", "password": "admin123", "nickname": "管理员"})
            print(">>> 创建默认管理员用户: admin/admin123")
        else:
            from database.crud import hash_password
            existing.password = hash_password("admin123")
            db.commit()
            print(">>> 更新默认管理员用户密码: admin/admin123")
    finally:
        db.close()

# 加载 .env 文件
load_dotenv()

# 优先使用 DATABASE_URL，回退到 DB_* 变量
DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL:
    SQLALCHEMY_DATABASE_URL = DATABASE_URL
else:
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "3306")
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "root")
    DB_NAME = os.getenv("DB_NAME", "study_system")
    SQLALCHEMY_DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# 创建数据库引擎
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True
)

# 创建数据库会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 所有数据表模型的基类
Base = declarative_base()

# FastAPI依赖函数，获取数据库会话
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 测试数据库连通性
if __name__ == "__main__":
    try:
        db_conn = next(get_db())
        print("✅ 数据库连接正常，第七步完成")
    except Exception as err:
        print(f"❌ 连接失败，错误信息：{err}")
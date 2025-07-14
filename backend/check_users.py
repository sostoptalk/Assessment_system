import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.main import SessionLocal, User

def check_users():
    """查看数据库中的用户"""
    db = SessionLocal()
    try:
        users = db.query(User).all()
        print("数据库中的用户:")
        for user in users:
            print(f"ID: {user.id}, 用户名: {user.username}, 真实姓名: {user.real_name}, 角色: {user.role}")
    finally:
        db.close()

if __name__ == "__main__":
    check_users() 
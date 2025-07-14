import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.main import SessionLocal, User, Paper

def test_db_connection():
    """测试数据库连接"""
    try:
        db = SessionLocal()
        print("数据库连接成功")
        
        # 测试查询用户
        users = db.query(User).limit(5).all()
        print(f"查询到 {len(users)} 个用户")
        
        # 测试查询试卷
        papers = db.query(Paper).limit(5).all()
        print(f"查询到 {len(papers)} 个试卷")
        
        db.close()
        print("数据库连接测试完成")
        return True
    except Exception as e:
        print(f"数据库连接失败: {str(e)}")
        import traceback
        print(f"详细错误: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    test_db_connection() 
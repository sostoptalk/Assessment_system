# -*- coding: utf-8 -*-
"""
直接操作数据库创建测试用户账号
使用bcrypt加密密码
"""
import pymysql
from passlib.context import CryptContext
from datetime import datetime

# 数据库配置
DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': 'Yrui2997',
    'database': 'test_assessment',
    'charset': 'utf8mb4'
}

# 密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    """生成密码哈希"""
    return pwd_context.hash(password)

def create_test_users_in_db():
    """在数据库中创建测试用户"""
    print("开始直接在数据库中创建测试用户...")
    print("=" * 50)
    
    # 测试用户列表
    test_users = [
        {
            "username": "admin",
            "password": "admin123",
            "real_name": "系统管理员",
            "role": "admin",
            "email": "admin@example.com",
            "phone": "13800138000"
        },
        {
            "username": "user1",
            "password": "user123",
            "real_name": "测试用户1",
            "role": "participant",
            "email": "user1@example.com",
            "phone": "13800138001"
        },
        {
            "username": "user2",
            "password": "user123",
            "real_name": "测试用户2",
            "role": "participant",
            "email": "user2@example.com",
            "phone": "13800138002"
        }
    ]
    
    try:
        # 连接数据库
        connection = pymysql.connect(**DB_CONFIG)
        cursor = connection.cursor()
        
        print("✅ 数据库连接成功")
        
        for user in test_users:
            print(f"正在创建用户: {user['username']}")
            
            # 检查用户是否已存在
            check_sql = "SELECT id FROM users WHERE username = %s"
            cursor.execute(check_sql, (user['username'],))
            existing_user = cursor.fetchone()
            
            if existing_user:
                print(f"⚠️  用户 {user['username']} 已存在，跳过创建")
                continue
            
            # 生成密码哈希
            password_hash = get_password_hash(user['password'])
            
            # 插入用户数据
            insert_sql = """
            INSERT INTO users (username, password_hash, real_name, role, email, phone, is_active, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            now = datetime.utcnow()
            cursor.execute(insert_sql, (
                user['username'],
                password_hash,
                user['real_name'],
                user['role'],
                user['email'],
                user['phone'],
                True,
                now,
                now
            ))
            
            user_id = cursor.lastrowid
            print(f"✅ 用户 {user['username']} 创建成功！用户ID: {user_id}")
            print("-" * 30)
        
        # 提交事务
        connection.commit()
        print("✅ 所有用户数据已提交到数据库")
        
    except pymysql.Error as e:
        print(f"❌ 数据库操作错误: {e}")
        if 'connection' in locals():
            connection.rollback()
    except Exception as e:
        print(f"❌ 创建用户时出现错误: {e}")
        if 'connection' in locals():
            connection.rollback()
    finally:
        if 'connection' in locals():
            cursor.close()
            connection.close()
            print("✅ 数据库连接已关闭")
    
    print("=" * 50)
    print("测试用户创建完成！")
    print("\n可用测试账号:")
    print("1. 管理员账号:")
    print("   用户名: admin")
    print("   密码: admin123")
    print("2. 普通用户账号:")
    print("   用户名: user1")
    print("   密码: user123")
    print("   用户名: user2")
    print("   密码: user123")

if __name__ == "__main__":
    create_test_users_in_db() 
import pymysql
import sys

# 数据库配置
DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': 'Yrui2997',
    'database': 'test_assessment',
    'charset': 'utf8mb4'
}

def migrate_database():
    """数据库迁移脚本"""
    try:
        # 连接数据库
        connection = pymysql.connect(**DB_CONFIG)
        cursor = connection.cursor()
        
        print("开始数据库迁移...")
        
        # 1. 检查并创建dimensions表
        print("1. 检查dimensions表...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS dimensions (
                id INT AUTO_INCREMENT PRIMARY KEY,
                paper_id INT NOT NULL,
                parent_id INT NULL,
                name VARCHAR(100) NOT NULL,
                description TEXT NULL,
                weight FLOAT DEFAULT 1.0,
                order_num INT DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (paper_id) REFERENCES papers(id) ON DELETE CASCADE,
                FOREIGN KEY (parent_id) REFERENCES dimensions(id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        print("dimensions表创建成功")
        
        # 2. 检查questions表是否有dimension_id字段
        print("2. 检查questions表的dimension_id字段...")
        cursor.execute("DESCRIBE questions")
        columns = [column[0] for column in cursor.fetchall()]
        
        if 'dimension_id' not in columns:
            print("添加dimension_id字段到questions表...")
            cursor.execute("""
                ALTER TABLE questions 
                ADD COLUMN dimension_id INT NULL,
                ADD FOREIGN KEY (dimension_id) REFERENCES dimensions(id) ON DELETE SET NULL
            """)
            print("dimension_id字段添加成功")
        else:
            print("dimension_id字段已存在")
        
        # 3. 检查paper_questions表是否有dimension_id字段
        print("3. 检查paper_questions表的dimension_id字段...")
        cursor.execute("DESCRIBE paper_questions")
        columns = [column[0] for column in cursor.fetchall()]
        
        if 'dimension_id' not in columns:
            print("添加dimension_id字段到paper_questions表...")
            cursor.execute("""
                ALTER TABLE paper_questions 
                ADD COLUMN dimension_id INT NULL,
                ADD FOREIGN KEY (dimension_id) REFERENCES dimensions(id) ON DELETE SET NULL
            """)
            print("dimension_id字段添加成功")
        else:
            print("dimension_id字段已存在")
        
        # 提交更改
        connection.commit()
        print("数据库迁移完成！")
        
    except Exception as e:
        print(f"数据库迁移失败: {e}")
        connection.rollback()
    finally:
        if 'connection' in locals():
            connection.close()

if __name__ == "__main__":
    migrate_database() 
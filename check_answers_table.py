import pymysql
import json

def check_answers_table():
    print("=" * 60)
    print("检查answers表数据")
    print("=" * 60)
    
    try:
        # 连接数据库
        connection = pymysql.connect(
            host='localhost',
            user='root',
            password='Yrui2997',
            database='test_assessment',
            charset='utf8mb4'
        )
        
        with connection.cursor() as cursor:
            # 1. 检查表结构
            print("\n1. 检查answers表结构...")
            cursor.execute("DESCRIBE answers")
            columns = cursor.fetchall()
            print("表结构:")
            for column in columns:
                print(f"  {column[0]}: {column[1]} {column[2]} {column[3]} {column[4]} {column[5]}")
            
            # 2. 检查表是否有数据
            print("\n2. 检查answers表数据...")
            cursor.execute("SELECT COUNT(*) FROM answers")
            count = cursor.fetchone()[0]
            print(f"总记录数: {count}")
            
            if count > 0:
                # 3. 查看最近的数据
                print("\n3. 查看最近的答题记录...")
                cursor.execute("""
                    SELECT a.id, a.user_id, a.question_id, a.answer, a.score, a.answered_at,
                           u.username, u.real_name, q.content
                    FROM answers a
                    LEFT JOIN users u ON a.user_id = u.id
                    LEFT JOIN questions q ON a.question_id = q.id
                    ORDER BY a.answered_at DESC
                    LIMIT 10
                """)
                records = cursor.fetchall()
                
                print("最近的答题记录:")
                for record in records:
                    print(f"  ID: {record[0]}")
                    print(f"  用户: {record[6]} ({record[7]})")
                    print(f"  题目ID: {record[2]}")
                    print(f"  题目内容: {record[8][:50]}..." if record[8] else "题目内容: 无")
                    print(f"  答案: {record[3]}")
                    print(f"  分数: {record[4]}")
                    print(f"  答题时间: {record[5]}")
                    print("  " + "-" * 40)
            else:
                print("❌ answers表中没有任何数据")
                
            # 4. 检查是否有用户答题
            print("\n4. 检查用户答题情况...")
            cursor.execute("""
                SELECT u.id, u.username, u.real_name, COUNT(a.id) as answer_count
                FROM users u
                LEFT JOIN answers a ON u.id = a.user_id
                WHERE u.role = 'participant'
                GROUP BY u.id, u.username, u.real_name
            """)
            users = cursor.fetchall()
            
            print("用户答题统计:")
            for user in users:
                print(f"  用户: {user[1]} ({user[2]}) - 答题数: {user[3]}")
            
            # 5. 检查试卷分配状态
            print("\n5. 检查试卷分配状态...")
            cursor.execute("""
                SELECT pa.id, pa.user_id, pa.paper_id, pa.status, pa.started_at, pa.completed_at,
                       u.username, u.real_name, p.name as paper_name
                FROM paper_assignments pa
                LEFT JOIN users u ON pa.user_id = u.id
                LEFT JOIN papers p ON pa.paper_id = p.id
                ORDER BY pa.assigned_at DESC
            """)
            assignments = cursor.fetchall()
            
            print("试卷分配状态:")
            for assignment in assignments:
                print(f"  分配ID: {assignment[0]}")
                print(f"  用户: {assignment[6]} ({assignment[7]})")
                print(f"  试卷: {assignment[8]}")
                print(f"  状态: {assignment[3]}")
                print(f"  开始时间: {assignment[4]}")
                print(f"  完成时间: {assignment[5]}")
                print("  " + "-" * 40)
                
    except Exception as e:
        print(f"❌ 检查数据库时出错: {str(e)}")
    finally:
        if 'connection' in locals():
            connection.close()

if __name__ == "__main__":
    check_answers_table() 
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.main import SessionLocal
from sqlalchemy import text

def check_user_scores():
    """检查测试用户6的答题记录和分数"""
    db = SessionLocal()
    try:
        user_id = 54  # 测试用户6
        paper_id = 10  # 管理潜质测评
        
        print(f"检查用户 {user_id} 在试卷 {paper_id} 的答题记录:")
        
        # 获取答题记录
        answers = db.execute(
            text("SELECT question_id, answer, score FROM answers WHERE user_id = :user_id"),
            {"user_id": user_id}
        ).fetchall()
        
        print(f"答题记录数量: {len(answers)}")
        
        # 显示前10条记录
        print("\n前10条答题记录:")
        for i, (question_id, answer, score) in enumerate(answers[:10]):
            print(f"  题目{question_id}: 答案={answer}, 分数={score}")
        
        # 统计分数分布
        scores = [score for _, _, score in answers]
        print(f"\n分数统计:")
        print(f"  最高分: {max(scores)}")
        print(f"  最低分: {min(scores)}")
        print(f"  平均分: {sum(scores) / len(scores):.2f}")
        print(f"  总分: {sum(scores)}")
        
        # 检查是否有10分的记录
        ten_scores = [score for score in scores if score == 10]
        print(f"  10分题目数量: {len(ten_scores)}")
        
    finally:
        db.close()

if __name__ == "__main__":
    check_user_scores() 
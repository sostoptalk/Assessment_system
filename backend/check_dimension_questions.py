import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.main import SessionLocal, Dimension, PaperQuestion
from sqlalchemy import text

def check_dimension_questions():
    """检查适应变化情境维度的题目映射"""
    db = SessionLocal()
    try:
        paper_id = 10
        
        # 查找"适应变化情境"维度
        dimension = db.query(Dimension).filter(
            Dimension.paper_id == paper_id,
            Dimension.name.like('%适应变化%')
        ).first()
        
        if dimension:
            print(f"找到维度: ID={dimension.id}, 名称={dimension.name}")
            
            # 查找该维度下的题目
            questions = db.query(PaperQuestion).filter(
                PaperQuestion.paper_id == paper_id,
                PaperQuestion.dimension_id == dimension.id
            ).all()
            
            print(f"该维度下的题目数量: {len(questions)}")
            for pq in questions:
                print(f"  题目ID: {pq.question_id}")
                
            # 检查用户54在该维度的答题记录
            user_id = 54
            answers = db.execute(
                text("""
                    SELECT a.question_id, a.answer, a.score 
                    FROM answers a
                    JOIN paper_questions pq ON a.question_id = pq.question_id
                    WHERE a.user_id = :user_id 
                    AND pq.paper_id = :paper_id 
                    AND pq.dimension_id = :dimension_id
                """),
                {"user_id": user_id, "paper_id": paper_id, "dimension_id": dimension.id}
            ).fetchall()
            
            print(f"\n用户54在该维度的答题记录:")
            for question_id, answer, score in answers:
                print(f"  题目{question_id}: 答案={answer}, 分数={score}")
                
            if answers:
                scores = [score for _, _, score in answers]
                print(f"  平均分: {sum(scores) / len(scores):.2f}")
            else:
                print("  没有找到答题记录")
        else:
            print("未找到包含'适应变化'的维度")
            
    finally:
        db.close()

if __name__ == "__main__":
    check_dimension_questions() 
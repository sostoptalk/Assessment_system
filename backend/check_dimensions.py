import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.main import SessionLocal, Dimension, PaperQuestion, Question

def check_dimensions():
    """检查试卷10的维度信息"""
    db = SessionLocal()
    try:
        paper_id = 10
        print(f"检查试卷 {paper_id} 的维度信息:")
        
        # 获取维度信息
        dimensions = db.query(Dimension).filter(Dimension.paper_id == paper_id).all()
        print(f"维度数量: {len(dimensions)}")
        for dim in dimensions:
            print(f"维度ID: {dim.id}, 名称: {dim.name}")
        
        # 获取题目-维度映射
        paper_questions = db.query(PaperQuestion).filter(PaperQuestion.paper_id == paper_id).all()
        print(f"\n题目-维度映射数量: {len(paper_questions)}")
        
        # 统计每个维度的题目数量
        dim_question_count = {}
        for pq in paper_questions:
            if pq.dimension_id:
                dim_name = next((d.name for d in dimensions if d.id == pq.dimension_id), "未知维度")
                if dim_name not in dim_question_count:
                    dim_question_count[dim_name] = 0
                dim_question_count[dim_name] += 1
        
        print("\n各维度题目数量:")
        for dim_name, count in dim_question_count.items():
            print(f"  {dim_name}: {count} 题")
            
    finally:
        db.close()

if __name__ == "__main__":
    check_dimensions() 
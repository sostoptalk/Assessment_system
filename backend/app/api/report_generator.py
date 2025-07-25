import os
import time
from sqlalchemy import text

# 将生成报告的逻辑分离到单独的文件中以避免循环引用
def generate_report_task(task_id, user_id, paper_id, report_tasks, SessionLocal):
    """
    生成报告的后台任务
    """
    # 在函数内部导入模型
    from app.main import User, Paper, PaperQuestion, Dimension, Report
    import sys
    sys.path.append(os.path.join(os.path.dirname(__file__), '../../reports/generators'))
    from reports.generators.report_core import generate_single_report
    
    db = SessionLocal()
    try:
        print(f"开始生成报告: task_id={task_id}, user_id={user_id}, paper_id={paper_id}")
        report_tasks[task_id]["status"] = "generating"
        report_tasks[task_id]["progress"] = 10
        # 1. 获取用户信息
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise Exception("用户不存在")
        print(f"用户信息: {user.real_name or user.username}")
        
        # 2. 获取试卷信息
        paper = db.query(Paper).filter(Paper.id == paper_id).first()
        if not paper:
            raise Exception("试卷不存在")
        print(f"试卷信息: {paper.name}")
        
        # 3. 获取答题记录
        answers = db.execute(
            text("SELECT question_id, answer, score FROM answers WHERE user_id = :user_id"),
            {"user_id": user_id}
        ).fetchall()
        answer_map = {row[0]: row[1] for row in answers}
        print(f"答题记录数量: {len(answer_map)}")
        
        # 4. 获取题目-维度映射
        paper_questions = db.query(PaperQuestion).filter(PaperQuestion.paper_id == paper_id).all()
        question_dim_map = {pq.question_id: pq.dimension_id for pq in paper_questions}
        print(f"题目-维度映射数量: {len(question_dim_map)}")
        
        # 5. 组装 report_data
        # 计算总分和维度分数
        total_score = 0
        dimension_scores = {}
        
        # 根据实际答题记录计算分数
        # 获取维度信息
        dimensions = db.query(Dimension).filter(Dimension.paper_id == paper_id).all()
        dimension_map = {dim.id: dim.name for dim in dimensions}
        
        # 构建维度层级结构
        big_dimensions = {}
        for dim in dimensions:
            if dim.parent_id is None:  # 大维度
                big_dimensions[dim.id] = {
                    "name": dim.name,
                    "score": 0,
                    "subs": {}
                }
        
        # 初始化所有子维度为0分
        for dim in dimensions:
            if dim.parent_id is not None:  # 子维度
                parent_dim = big_dimensions.get(dim.parent_id)
                if parent_dim:
                    parent_dim["subs"][dim.name] = 0
        
        # 按维度分组计算分数
        dimension_question_scores = {}
        for question_id, answer, score in answers:
            if question_id in question_dim_map:
                dim_id = question_dim_map[question_id]
                if dim_id in dimension_map:
                    dim_name = dimension_map[dim_id]
                    if dim_name not in dimension_question_scores:
                        dimension_question_scores[dim_name] = []
                    dimension_question_scores[dim_name].append(score)
        
        # 计算每个维度的平均分并组织层级结构
        for dim_name, scores in dimension_question_scores.items():
            if scores:
                avg_score = sum(scores) / len(scores)
                
                # 找到对应的维度对象
                dim_obj = next((dim for dim in dimensions if dim.name == dim_name), None)
                if dim_obj:
                    if dim_obj.parent_id is None:  # 大维度
                        big_dimensions[dim_obj.id]["score"] = avg_score
                    else:  # 子维度
                        parent_dim = big_dimensions.get(dim_obj.parent_id)
                        if parent_dim:
                            parent_dim["subs"][dim_name] = avg_score
        
        # 计算大维度的平均分（基于子维度）
        for big_dim in big_dimensions.values():
            if big_dim["subs"]:
                big_dim["score"] = sum(big_dim["subs"].values()) / len(big_dim["subs"])
        
        # 转换为最终格式
        dimension_scores = {}
        for big_dim in big_dimensions.values():
            dimension_scores[big_dim["name"]] = {
                "score": big_dim["score"],
                "subs": big_dim["subs"]
            }
        
        # 计算总分（所有大维度的平均分）
        if dimension_scores:
            total_score = sum(dim["score"] for dim in dimension_scores.values()) / len(dimension_scores)
        
        print(f"计算得到的维度分数: {dimension_scores}")
        print(f"计算得到的总分: {total_score}")
        
        report_data = {
            "user_info": {
                "id": user.id,
                "name": user.real_name or user.username,
                "username": user.username,
                "total_score": total_score
            },
            "paper_info": {
                "id": paper.id,
                "name": paper.name,
                "description": paper.description
            },
            "dimensions": dimension_scores,
            "answers": answer_map,
            "question_dim_map": question_dim_map
        }
        
        print(f"报告数据组装完成，开始生成PDF...")
        
        # 6. 生成PDF
        from pathlib import Path
        output_dir = Path(__file__).parent.parent.parent / "reports" / "generators" / "output"
        output_dir.mkdir(parents=True, exist_ok=True)
        safe_name = (user.real_name or user.username or "user")
        output_filename = f"{safe_name}_报告_{paper_id}_{user_id}_{int(time.time())}.pdf"
        output_path = str(output_dir / output_filename)
        
        print(f"PDF输出路径: {output_path}")
        generate_single_report(paper_id, report_data, output_path)
        
        print(f"PDF生成成功: {output_path}")
        
        # 保存报告到数据库
        import os
        
        # 计算文件大小
        file_size = os.path.getsize(output_path) if os.path.exists(output_path) else 0
        
        # 创建报告记录
        report = Report(
            user_id=user_id,
            paper_id=paper_id,
            file_path=output_path,
            file_name=output_filename,
            file_size=file_size,
            status="completed"
        )
        db.add(report)
        db.commit()
        db.refresh(report)
        
        report_tasks[task_id]["status"] = "completed"
        report_tasks[task_id]["progress"] = 100
        report_tasks[task_id]["file_path"] = output_path
        report_tasks[task_id]["report_id"] = report.id
    except Exception as e:
        print(f"生成报告失败: {str(e)}")
        import traceback
        print(f"详细错误: {traceback.format_exc()}")
        report_tasks[task_id]["status"] = "failed"
        report_tasks[task_id]["error_message"] = str(e)
        report_tasks[task_id]["progress"] = 100
    finally:
        db.close() 
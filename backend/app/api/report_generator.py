import os
import time
from sqlalchemy import text

# 将生成报告的逻辑分离到单独的文件中以避免循环引用
def generate_report_task(task_id, user_id, paper_id, report_tasks, SessionLocal):
    """
    生成报告的后台任务
    """
    # 确保os模块在函数开始时就可用
    import os
    import traceback
    
    # 在函数内部导入模型
    print(f"[DEBUG] 进入报告生成任务: task_id={task_id}, user_id={user_id}, paper_id={paper_id}")
    
    try:
        from app.main import User, Paper, PaperQuestion, Dimension, Report
        print(f"[DEBUG] 成功导入数据库模型")
        
        import sys
        current_dir = os.path.dirname(os.path.abspath(__file__))
        generators_path = os.path.join(current_dir, '../../reports/generators')
        print(f"[DEBUG] 添加路径到sys.path: {generators_path}")
        sys.path.append(generators_path)
        
        try:
            from reports.generators.report_core import generate_single_report
            print(f"[DEBUG] 成功导入report_core.generate_single_report")
        except ImportError as e:
            print(f"[ERROR] 导入report_core失败: {str(e)}")
            import traceback
            print(f"[ERROR] 导入错误详情: {traceback.format_exc()}")
            raise
    except Exception as e:
        print(f"[ERROR] 初始化报告生成任务失败: {str(e)}")
        import traceback
        print(f"[ERROR] 初始化错误详情: {traceback.format_exc()}")
        report_tasks[task_id]["status"] = "failed"
        report_tasks[task_id]["error_message"] = f"初始化失败: {str(e)}"
        report_tasks[task_id]["progress"] = 100
        return
    
    db = SessionLocal()
    try:
        print(f"[DEBUG] 开始生成报告: task_id={task_id}, user_id={user_id}, paper_id={paper_id}")
        report_tasks[task_id]["status"] = "generating"
        report_tasks[task_id]["progress"] = 10
        # 1. 获取用户信息
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                raise Exception("用户不存在")
            print(f"[DEBUG] 用户信息: ID={user.id}, 姓名={user.real_name or user.username}")
        except Exception as e:
            print(f"[ERROR] 获取用户信息失败: {str(e)}")
            raise Exception(f"获取用户信息失败: {str(e)}")
        
        # 2. 获取试卷信息
        try:
            paper = db.query(Paper).filter(Paper.id == paper_id).first()
            if not paper:
                raise Exception("试卷不存在")
            print(f"[DEBUG] 试卷信息: ID={paper.id}, 名称={paper.name}")
        except Exception as e:
            print(f"[ERROR] 获取试卷信息失败: {str(e)}")
            raise Exception(f"获取试卷信息失败: {str(e)}")
        
        # 3. 获取答题记录
        try:
            answers = db.execute(
                text("SELECT question_id, answer, score FROM answers WHERE user_id = :user_id"),
                {"user_id": user_id}
            ).fetchall()
            answer_map = {row[0]: row[1] for row in answers}
            print(f"[DEBUG] 答题记录数量: {len(answer_map)}")
            if len(answer_map) == 0:
                print(f"[WARNING] 用户 {user_id} 没有答题记录!")
        except Exception as e:
            print(f"[ERROR] 获取答题记录失败: {str(e)}")
            import traceback
            print(f"[ERROR] 获取答题记录错误详情: {traceback.format_exc()}")
            raise Exception(f"获取答题记录失败: {str(e)}")
        
        # 4. 获取题目-维度映射
        try:
            paper_questions = db.query(PaperQuestion).filter(PaperQuestion.paper_id == paper_id).all()
            question_dim_map = {pq.question_id: pq.dimension_id for pq in paper_questions}
            print(f"[DEBUG] 题目-维度映射数量: {len(question_dim_map)}")
            if len(question_dim_map) == 0:
                print(f"[WARNING] 试卷 {paper_id} 没有题目-维度映射!")
        except Exception as e:
            print(f"[ERROR] 获取题目-维度映射失败: {str(e)}")
            import traceback
            print(f"[ERROR] 获取题目-维度映射错误详情: {traceback.format_exc()}")
            raise Exception(f"获取题目-维度映射失败: {str(e)}")
        
        # 5. 组装 report_data
        # 计算总分和维度分数
        total_score = 0
        dimension_scores = {}
        
        # 根据实际答题记录计算分数
        # 获取维度信息
        try:
            dimensions = db.query(Dimension).filter(Dimension.paper_id == paper_id).all()
            print(f"[DEBUG] 获取到维度数量: {len(dimensions)}")
            if len(dimensions) == 0:
                print(f"[WARNING] 试卷 {paper_id} 没有维度定义!")
            dimension_map = {dim.id: dim.name for dim in dimensions}
        except Exception as e:
            print(f"[ERROR] 获取维度信息失败: {str(e)}")
            import traceback
            print(f"[ERROR] 获取维度信息错误详情: {traceback.format_exc()}")
            raise Exception(f"获取维度信息失败: {str(e)}")
        
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
        total_score = 0
        if dimension_scores:
            total_score = sum(dim["score"] for dim in dimension_scores.values()) / len(dimension_scores)

        print(f"[DEBUG] 计算得到的维度分数: {dimension_scores}")
        print(f"[DEBUG] 计算得到的总分: {total_score}")
        
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
        
        print(f"[DEBUG] 报告数据组装完成，开始生成PDF...")
        
        # 6. 生成PDF
        try:
            from pathlib import Path
            output_dir = Path(__file__).parent.parent.parent / "reports" / "generators" / "output"
            print(f"[DEBUG] 输出目录: {output_dir}")
            output_dir.mkdir(parents=True, exist_ok=True)
            safe_name = (user.real_name or user.username or "user")
            output_filename = f"{safe_name}_报告_{paper_id}_{user_id}_{int(time.time())}.pdf"
            output_path = str(output_dir / output_filename)
            
            print(f"[DEBUG] PDF输出路径: {output_path}")
            
            # 检查配置文件是否存在
            config_path = Path(__file__).parent.parent.parent / "reports" / "generators" / "configs" / f"{paper_id}.yaml"
            print(f"[DEBUG] 配置文件路径: {config_path}, 存在: {config_path.exists()}")

            # 如果配置文件不存在，尝试在备选路径查找
            if not config_path.exists():
                alt_config_path = Path(__file__).parent.parent.parent / "backend" / "reports" / "generators" / "configs" / f"{paper_id}.yaml"
                if alt_config_path.exists():
                    print(f"[DEBUG] 在备选路径找到配置文件: {alt_config_path}")
                    # 复制到正确位置
                    import shutil
                    try:
                        shutil.copy2(alt_config_path, config_path)
                        print(f"[DEBUG] 已将配置文件从 {alt_config_path} 复制到 {config_path}")
                    except Exception as copy_error:
                        print(f"[ERROR] 复制配置文件失败: {str(copy_error)}")

            # 再次检查配置文件是否存在
            if not config_path.exists():
                raise Exception(f"配置文件不存在: {config_path}")

            # 调用报告生成函数
            print(f"[DEBUG] 调用generate_single_report函数: paper_id={paper_id}")
            generate_single_report(paper_id, report_data, output_path)
            
            print(f"[DEBUG] PDF生成成功: {output_path}")
        except Exception as e:
            print(f"[ERROR] 生成PDF失败: {str(e)}")
            import traceback
            print(f"[ERROR] 生成PDF错误详情: {traceback.format_exc()}")
            raise Exception(f"生成PDF失败: {str(e)}")
        
        # 保存报告到数据库
        try:
            import os
            
            # 计算文件大小
            if os.path.exists(output_path):
                file_size = os.path.getsize(output_path)
                print(f"[DEBUG] 文件存在，大小: {file_size} 字节")
            else:
                file_size = 0
                print(f"[WARNING] 文件不存在: {output_path}")
            
            # 创建报告记录
            print(f"[DEBUG] 创建报告记录: user_id={user_id}, paper_id={paper_id}")
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
            print(f"[DEBUG] 报告记录创建成功，ID: {report.id}")
            
            # 更新任务状态
            print(f"[DEBUG] 更新任务状态为已完成: task_id={task_id}")
            report_tasks[task_id]["status"] = "completed"
            report_tasks[task_id]["progress"] = 100
            report_tasks[task_id]["file_path"] = output_path
            report_tasks[task_id]["report_id"] = report.id
        except Exception as e:
            print(f"[ERROR] 保存报告记录失败: {str(e)}")
            import traceback
            print(f"[ERROR] 保存报告记录错误详情: {traceback.format_exc()}")
            raise Exception(f"保存报告记录失败: {str(e)}")
    except Exception as e:
        print(f"[ERROR] 生成报告失败: {str(e)}")
        import traceback
        print(f"[ERROR] 详细错误: {traceback.format_exc()}")
        try:
            report_tasks[task_id]["status"] = "failed"
            report_tasks[task_id]["error_message"] = str(e)
            report_tasks[task_id]["progress"] = 100
            print(f"[DEBUG] 已更新任务状态为失败: task_id={task_id}")
        except Exception as ex:
            print(f"[ERROR] 更新任务状态失败: {str(ex)}")
    finally:
        try:
            db.close()
            print(f"[DEBUG] 数据库连接已关闭")
        except Exception as e:
            print(f"[ERROR] 关闭数据库连接失败: {str(e)}")
        print(f"[DEBUG] 报告生成任务完成: task_id={task_id}") 
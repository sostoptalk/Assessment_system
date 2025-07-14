import os
import json
from pathlib import Path
from fastapi import HTTPException
from datetime import datetime
# Change this line:
from backend.reports.generators.report_generator_v2 import generate_business_report

# To this line (remove 'backend.' prefix):
from reports.generators.report_generator_v2 import generate_business_report

class ReportService:
    def __init__(self, db):
        self.db = db
        self.report_dir = Path("reports")
        self.report_dir.mkdir(exist_ok=True)
        self.template_path = Path("backend/reports/templates/report_template.html")
        self.dimension_data_path = Path("backend/reports/data/dimension_data.json")

    def get_dimension_data(self):
        if not self.dimension_data_path.exists():
            raise HTTPException(status_code=404, detail="维度数据文件不存在")
        with open(self.dimension_data_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def calculate_individual_data(self, user_id, assignment_id):
        # 从answers表计算用户各维度得分
        from sqlalchemy import func
        from app.main import Answer, Question, PaperQuestion, Dimension

        # 查询用户该次测试的所有答案
        answers = self.db.query(
            Question.dimension_id, 
            func.sum(Answer.score).label('total_score')
        ).join(
            PaperQuestion, PaperQuestion.question_id == Question.id
        ).join(
            Answer, Answer.question_id == Question.id
        ).filter(
            Answer.user_id == user_id,
            PaperQuestion.assignment_id == assignment_id
        ).group_by(Question.dimension_id).all()

        # 组织维度得分数据
        dimensions = {}
        for dim_id, score in answers:
            dimension = self.db.query(Dimension).filter(Dimension.id == dim_id).first()
            if dimension:
                dimensions[dimension.name] = {"score": round(score, 2)}

        # 获取用户总分
        total_score = sum(score for _, score in answers)

        return {
            "user_info": {
                "name": self.db.query(User).filter(User.id == user_id).first().real_name,
                "total_score": round(total_score, 2)
            },
            "dimensions": dimensions
        }

    def calculate_average_data(self, paper_id):
        # 计算所有用户该试卷的平均得分
        from sqlalchemy import func
        from app.main import Answer, Question, PaperQuestion, Dimension, PaperAssignment

        # 获取所有已完成该试卷的用户
        completed_assignments = self.db.query(PaperAssignment).filter(
            PaperAssignment.paper_id == paper_id,
            PaperAssignment.status == "completed"
        ).all()
        user_ids = [a.user_id for a in completed_assignments]

        if not user_ids:
            return self._get_empty_average_data(paper_id)

        # 计算每个维度的平均分
        dim_scores = self.db.query(
            Question.dimension_id,
            func.avg(Answer.score).label('avg_score')
        ).join(
            PaperQuestion, PaperQuestion.question_id == Question.id
        ).join(
            Answer, Answer.question_id == Question.id
        ).filter(
            PaperQuestion.paper_id == paper_id,
            Answer.user_id.in_(user_ids)
        ).group_by(Question.dimension_id).all()

        # 组织维度得分数据
        dimensions = {}
        total_score = 0
        count = 0
        for dim_id, avg_score in dim_scores:
            dimension = self.db.query(Dimension).filter(Dimension.id == dim_id).first()
            if dimension:
                score = round(float(avg_score), 2)
                dimensions[dimension.name] = {"score": score}
                total_score += score
                count += 1

        avg_total_score = round(total_score / count, 2) if count > 0 else 0

        return {
            "user_info": {
                "name": "average",
                "total_score": avg_total_score
            },
            "dimensions": dimensions
        }

    def _get_empty_average_data(self, paper_id):
        # 获取试卷所有维度
        from app.main import Dimension
        dimensions = self.db.query(Dimension).filter(Dimension.paper_id == paper_id).all()
        dim_data = {dim.name: {"score": 0} for dim in dimensions}
        return {
            "user_info": {
                "name": "average",
                "total_score": 0
            },
            "dimensions": dim_data
        }

    def get_user_reports(self, user_id):
        # 获取用户的所有报告
        from app.models.report import Report
        return self.db.query(Report).filter(Report.user_id == user_id).all()

    def get_report_by_id(self, report_id, user_id=None):
        # 获取单个报告
        from app.models.report import Report
        query = self.db.query(Report).filter(Report.id == report_id)
        if user_id:
            query = query.filter(Report.user_id == user_id)
        return query.first()

    def generate_report(self, user_id, assignment_id):
        # 获取试卷分配信息
        assignment = self.db.query(PaperAssignment).filter(
            PaperAssignment.id == assignment_id,
            PaperAssignment.user_id == user_id
        ).first()

        if not assignment or assignment.status != "completed":
            raise HTTPException(status_code=400, detail="测试未完成，无法生成报告")

        # 计算个人和平均数据
        individual_data = self.calculate_individual_data(user_id, assignment_id)
        average_data = self.calculate_average_data(assignment.paper_id)

        # 生成报告文件名
        user = self.db.query(User).filter(User.id == user_id).first()
        user_name = user.real_name or user.username
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{user_name}_报告_{timestamp}.pdf"
        output_path = str(self.report_dir / filename)

        # 调用现有报告生成器
        generate_business_report(
            individual_data=individual_data,
            average_data=average_data,
            output_path=output_path,
            template_path=str(self.template_path)
        )

        # 计算文件大小
        file_size = os.path.getsize(output_path) if os.path.exists(output_path) else 0

        # 保存报告记录到数据库
        from app.models.report import Report
        report = Report(
            user_id=user_id,
            paper_id=assignment.paper_id,
            file_path=output_path,
            file_name=filename,
            file_size=file_size,
            status="completed"
        )
        self.db.add(report)
        self.db.commit()
        self.db.refresh(report)

        return report
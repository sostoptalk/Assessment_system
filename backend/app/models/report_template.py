from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.main import Base


class ReportTemplate(Base):
    """报告模板模型"""
    __tablename__ = "report_templates"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(200), nullable=False, comment="模板名称")
    paper_id = Column(Integer, ForeignKey("papers.id"), nullable=False, comment="关联试卷ID")
    config = Column(Text, nullable=False, comment="模板配置（JSON格式）")
    yaml_config = Column(Text, nullable=False, comment="模板配置（YAML格式）")
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # 关系
    paper = relationship("Paper", back_populates="report_templates") 
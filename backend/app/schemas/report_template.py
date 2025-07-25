from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime


class ReportTemplateBase(BaseModel):
    """报告模板基础Schema"""
    name: str
    paper_id: int


class ReportTemplateCreate(ReportTemplateBase):
    """创建报告模板Schema"""
    config: Dict[str, Any]
    yaml_config: str


class ReportTemplateUpdate(BaseModel):
    """更新报告模板Schema"""
    name: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    yaml_config: Optional[str] = None


class ReportTemplateResponse(ReportTemplateBase):
    """报告模板响应Schema"""
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True


class ReportTemplateDetail(ReportTemplateResponse):
    """报告模板详情Schema"""
    config: Dict[str, Any]
    yaml_config: str


class ReportTemplatePreview(BaseModel):
    """报告模板预览Schema"""
    config: Dict[str, Any]
    yaml_config: str
    test_data: Optional[Dict[str, Any]] = None 
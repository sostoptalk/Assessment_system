from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
import json

from app.services.report_template_service import report_template_service
from app.schemas.report_template import (
    ReportTemplateCreate,
    ReportTemplateUpdate,
    ReportTemplateResponse,
    ReportTemplateDetail,
    ReportTemplatePreview
)
from app.main import get_db

router = APIRouter(
    prefix="/report-templates",
    tags=["report-templates"],
    responses={404: {"description": "Not found"}},
)

@router.post("/", response_model=ReportTemplateResponse)
async def create_report_template(template: ReportTemplateCreate, db: Session = Depends(get_db)):
    """创建新的报告模板"""
    return report_template_service.create_report_template(db, template)

@router.get("/", response_model=List[ReportTemplateResponse])
async def get_report_templates(paper_id: Optional[int] = None, db: Session = Depends(get_db)):
    """获取报告模板列表"""
    return report_template_service.get_report_templates(db, paper_id)

@router.post("/preview", response_model=None)
async def preview_report_template(template_data: Dict[str, Any] = Body(...)):
    """预览报告模板"""
    try:
        print("开始生成预览...")
        print(f"接收到的模板数据键: {template_data.keys()}")
        
        # 检查template_id
        template_id = template_data.get('template_id')
        if template_id and 'config' not in template_data:
            print(f"使用模板ID {template_id} 获取配置")
            try:
                # 获取数据库会话
                from app.main import get_db_session
                db = next(get_db_session())
                
                # 获取模板
                template = report_template_service.get_report_template(db, template_id)
                
                # 解析配置
                config = json.loads(template.config) if isinstance(template.config, str) else template.config
                
                # 更新请求数据
                template_data['config'] = config
                template_data['yaml_config'] = template.yaml_config or ''
                
                print(f"成功从数据库获取模板 {template.name} 的配置")
            except Exception as e:
                print(f"获取模板配置失败: {str(e)}")
        
        # 检查必要的字段
        if 'config' not in template_data:
            print("错误: 缺少config字段")
            raise HTTPException(
                status_code=400,
                detail="缺少config字段，请提供HTML模板内容"
            )
        
        # 创建测试数据（默认值）
        test_data = {
            "user_info": {
                "name": "测试用户",
                "total_score": 7.8
            },
            "dimensions": [
                {"name": "维度1", "score": 8.5, "subs": {}},
                {"name": "维度2", "score": 7.2, "subs": {}},
                {"name": "维度3", "score": 6.7, "subs": {}}
            ],
            "performance_eval": {
                "summary": "表现良好，具备发展潜力",
                "development_focus": "建议加强专业技能培训"
            },
            "chart_img": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="
        }
        
        # 处理请求数据
        preview_html = report_template_service.generate_preview(template_data, test_data)
        
        if not preview_html or not isinstance(preview_html, str):
            print(f"预览生成失败: 返回内容类型 {type(preview_html)}")
            raise HTTPException(
                status_code=500, 
                detail="生成预览失败：无效的HTML内容"
            )
        
        # 返回HTML响应
        from fastapi.responses import HTMLResponse
        print(f"预览生成成功，内容长度: {len(preview_html)}")
        return HTMLResponse(content=preview_html, media_type="text/html")
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print(f"生成预览失败: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail=f"生成预览失败: {str(e)}"
        )

@router.get("/paper/{paper_id}", response_model=List[ReportTemplateResponse])
async def get_templates_by_paper(paper_id: int, db: Session = Depends(get_db)):
    """获取指定试卷的报告模板"""
    return report_template_service.get_report_templates(db, paper_id)

@router.get("/components")
async def get_template_components(component_type: Optional[str] = None):
    """获取模板组件库"""
    return report_template_service.get_template_components(component_type)

@router.post("/generate-from-components")
async def generate_from_components(components: List[Dict[str, str]] = Body(...)):
    """根据组件列表生成模板HTML"""
    return report_template_service.generate_template_from_components(components)

@router.get("/default-template", response_model=None)
async def get_default_template():
    """获取默认模板HTML"""
    try:
        print("正在生成默认模板...")
        template_html = report_template_service.generate_default_template()
        
        if not template_html:
            print("错误: 生成的模板为空")
            raise HTTPException(
                status_code=500, 
                detail="生成默认模板失败：模板生成器返回了空内容"
            )
            
        if not isinstance(template_html, str):
            print(f"错误: 生成的模板不是字符串类型，而是 {type(template_html)}")
            raise HTTPException(
                status_code=500, 
                detail=f"生成默认模板失败：模板类型错误，期望字符串但收到 {type(template_html)}"
            )
            
        # 返回纯文本内容
        from fastapi.responses import PlainTextResponse
        print(f"成功生成模板，内容长度: {len(template_html)}")
        return PlainTextResponse(content=template_html, media_type="text/html")
    except Exception as e:
        import traceback
        error_stack = traceback.format_exc()
        print(f"获取默认模板时出错: {str(e)}")
        print(f"错误堆栈: {error_stack}")
        raise HTTPException(
            status_code=500,
            detail=f"获取默认模板失败: {str(e)}"
        )

# 这些通用路径参数路由必须放在特定路径之后
@router.get("/{template_id}", response_model=ReportTemplateDetail)
async def get_report_template(template_id: int, db: Session = Depends(get_db)):
    """获取单个报告模板详情"""
    return report_template_service.get_report_template(db, template_id)

@router.put("/{template_id}", response_model=ReportTemplateResponse)
async def update_report_template(template_id: int, template: ReportTemplateUpdate, db: Session = Depends(get_db)):
    """更新报告模板"""
    return report_template_service.update_report_template(db, template_id, template)

@router.delete("/{template_id}")
async def delete_report_template(template_id: int, db: Session = Depends(get_db)):
    """删除报告模板"""
    result = report_template_service.delete_report_template(db, template_id)
    if result:
        return {"message": "报告模板已删除"}
    return {"message": "删除报告模板失败"} 
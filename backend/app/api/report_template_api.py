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
            preview_html = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>预览生成失败</title>
</head>
<body>
    <h1>预览生成失败：无效的HTML内容</h1>
</body>
</html>"""
        
        # 检查HTML内容是否太短（可能是无效内容）
        if len(preview_html) < 200:  # 如果返回的HTML内容太短
            print(f"警告: 返回的HTML内容太短({len(preview_html)}字符)，可能无法正常显示，使用备用HTML")
            preview_html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>报告预览</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        h1 {{ color: #333; }}
        .container {{ 
            border: 1px solid #ddd; 
            padding: 20px; 
            border-radius: 5px;
            background-color: #f9f9f9;
        }}
        .highlight {{ 
            background-color: #e1f5fe; 
            padding: 10px; 
            margin: 20px 0;
            border-left: 4px solid #03a9f4;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>测评报告预览</h1>
        <p>这是一个测试报告预览，原始HTML内容长度为: {len(preview_html)}字符</p>
        
        <div class="highlight">
            <h2>预览内容示例</h2>
            <p>姓名: 测试用户</p>
            <p>总分: 7.8</p>
            <p>评价: 表现良好，具备发展潜力</p>
        </div>
        
        <h3>原始HTML内容:</h3>
        <pre>{preview_html}</pre>
    </div>
</body>
</html>"""
        
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
        
        # 返回错误HTML而不是抛出异常
        from fastapi.responses import HTMLResponse
        error_html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>预览生成错误</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        h1 {{ color: #d32f2f; }}
        .error {{ 
            background-color: #ffebee; 
            padding: 20px; 
            border-left: 4px solid #d32f2f;
            margin: 20px 0;
        }}
        pre {{ background: #f5f5f5; padding: 10px; overflow: auto; }}
    </style>
</head>
<body>
    <h1>报告预览生成失败</h1>
    <div class="error">
        <h2>错误信息:</h2>
        <p>{str(e)}</p>
    </div>
    <h3>错误堆栈:</h3>
    <pre>{traceback.format_exc()}</pre>
</body>
</html>"""
        return HTMLResponse(content=error_html, media_type="text/html")

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

# 添加模板设计器相关API
@router.post("/designer-templates", response_model=dict)
async def create_designer_template(template_data: Dict[str, Any] = Body(...), db: Session = Depends(get_db)):
    """保存设计器模板到库中"""
    try:
        result = report_template_service.create_designer_template(db, template_data)
        return {"success": True, "id": result.id, "message": "模板保存成功"}
    except Exception as e:
        import traceback
        print(f"保存设计器模板失败: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"保存设计器模板失败: {str(e)}")

@router.get("/designer-templates", response_model=List[Dict[str, Any]])
async def get_designer_templates(db: Session = Depends(get_db)):
    """获取设计器模板列表"""
    try:
        templates = report_template_service.get_designer_templates(db)
        return [{"id": t.id, "name": t.name, "created_at": t.created_at} for t in templates]
    except Exception as e:
        print(f"获取设计器模板列表失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取设计器模板列表失败: {str(e)}")

@router.get("/designer-templates/{template_id}", response_model=Dict[str, Any])
async def get_designer_template(template_id: int, db: Session = Depends(get_db)):
    """获取单个设计器模板详情"""
    try:
        template = report_template_service.get_designer_template(db, template_id)
        if not template:
            raise HTTPException(status_code=404, detail=f"模板ID {template_id} 不存在")
            
        # 解析配置，确保组件字段是可用的
        config = json.loads(template.config) if isinstance(template.config, str) else template.config
        components = config.get('components', [])
        
        return {
            "id": template.id,
            "name": template.name,
            "components": components,
            "html_content": config.get('html_content', ''),
            "created_at": template.created_at
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"获取设计器模板详情失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取设计器模板详情失败: {str(e)}")

@router.delete("/designer-templates/{template_id}")
async def delete_designer_template(template_id: int, db: Session = Depends(get_db)):
    """删除设计器模板"""
    try:
        result = report_template_service.delete_designer_template(db, template_id)
        if result:
            return {"message": "设计器模板已删除"}
        return {"message": "删除设计器模板失败"}
    except Exception as e:
        print(f"删除设计器模板失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"删除设计器模板失败: {str(e)}") 
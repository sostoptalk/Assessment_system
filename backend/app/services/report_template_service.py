import os
import json
from pathlib import Path
from fastapi import HTTPException
import yaml
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional, List

from app.models.report_template import ReportTemplate
from app.schemas.report_template import ReportTemplateCreate, ReportTemplateUpdate
from reports.generators.generate_report import generate_preview_html
from reports.generators.template_components import (
    get_component, get_components_by_type, 
    generate_template_with_components, generate_default_template
)

class ReportTemplateService:
    def __init__(self):
        self.template_base_path = Path("backend/reports/generators/templates")
        self.template_base_path.mkdir(exist_ok=True, parents=True)
        self.config_base_path = Path("backend/reports/generators/configs")
        self.config_base_path.mkdir(exist_ok=True, parents=True)

    def create_report_template(self, db: Session, template: ReportTemplateCreate) -> ReportTemplate:
        """创建新的报告模板"""
        # 将Python字典转换为JSON字符串
        config_json = json.dumps(template.config, ensure_ascii=False)
        
        # 创建新模板记录
        db_template = ReportTemplate(
            name=template.name,
            paper_id=template.paper_id,
            config=config_json,
            yaml_config=template.yaml_config
        )
        
        db.add(db_template)
        db.commit()
        db.refresh(db_template)
        
        # 保存模板文件到磁盘
        self._save_template_files(db_template)
        
        return db_template
    
    def get_report_templates(self, db: Session, paper_id: Optional[int] = None) -> List[ReportTemplate]:
        """获取报告模板列表"""
        query = db.query(ReportTemplate)
        
        if paper_id is not None:
            query = query.filter(ReportTemplate.paper_id == paper_id)
            
        return query.all()
    
    def get_report_template(self, db: Session, template_id: int) -> ReportTemplate:
        """获取单个报告模板详情"""
        try:
            print(f"正在获取模板ID: {template_id}")
            template = db.query(ReportTemplate).filter(ReportTemplate.id == template_id).first()
            if not template:
                print(f"模板ID {template_id} 不存在")
                raise HTTPException(status_code=404, detail=f"报告模板ID {template_id} 不存在")
            
            print(f"成功获取模板: {template.name}")
            return template
        except HTTPException:
            raise
        except Exception as e:
            import traceback
            print(f"获取模板 {template_id} 时出错: {str(e)}")
            print(traceback.format_exc())
            raise HTTPException(
                status_code=500,
                detail=f"获取报告模板失败: {str(e)}"
            )
    
    def update_report_template(self, db: Session, template_id: int, template_update: ReportTemplateUpdate) -> ReportTemplate:
        """更新报告模板"""
        db_template = self.get_report_template(db, template_id)
        
        update_data = template_update.dict(exclude_unset=True)
        
        # 处理配置字段，确保是JSON字符串
        if 'config' in update_data:
            if isinstance(update_data['config'], dict):
                update_data['config'] = json.dumps(update_data['config'], ensure_ascii=False)
        
        # 更新模板记录
        for key, value in update_data.items():
            setattr(db_template, key, value)
        
        db.add(db_template)
        db.commit()
        db.refresh(db_template)
        
        # 更新文件
        self._save_template_files(db_template)
        
        return db_template
    
    def delete_report_template(self, db: Session, template_id: int) -> bool:
        """删除报告模板"""
        db_template = self.get_report_template(db, template_id)
        
        # 删除模板记录
        db.delete(db_template)
        db.commit()
        
        # 尝试删除对应文件
        try:
            # 删除模板文件
            config = json.loads(db_template.config)
            template_name = config.get('template', {}).get('name')
            if template_name:
                template_path = self.template_base_path / template_name
                if template_path.exists():
                    template_path.unlink()
            
            # 删除配置文件
            config_path = self.config_base_path / f"{db_template.paper_id}.yaml"
            if config_path.exists():
                config_path.unlink()
                
        except Exception as e:
            print(f"删除模板文件失败: {str(e)}")
            
        return True
    
    def generate_preview(self, template_data: Dict[str, Any], test_data: Optional[Dict[str, Any]] = None) -> str:
        """生成模板预览HTML"""
        try:
            print(f"生成预览，模板数据键: {template_data.keys()}")
            
            # 检查是否使用模板ID预览
            template_id = template_data.get('template_id')
            if template_id:
                print(f"使用模板ID预览: {template_id}")
                try:
                    from sqlalchemy.orm import Session
                    from app.main import get_db_session
                    
                    # 获取数据库会话
                    db: Session = next(get_db_session())
                    
                    # 获取模板详情
                    template = self.get_report_template(db, template_id)
                    
                    if not template:
                        print(f"错误: 未找到ID为{template_id}的模板")
                        raise HTTPException(status_code=404, detail=f"未找到ID为{template_id}的模板")
                    
                    # 解析配置
                    config = json.loads(template.config) if isinstance(template.config, str) else template.config
                    yaml_config = template.yaml_config
                    
                    # 更新模板数据
                    template_data['config'] = config
                    template_data['yaml_config'] = yaml_config
                    
                    print(f"成功获取模板配置: {template.name}")
                except Exception as e:
                    print(f"获取模板详情失败: {str(e)}")
                    return f"""<!DOCTYPE html>
<html>
<head>
    <title>模板加载错误</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .error {{ color: red; padding: 10px; border: 1px solid red; border-radius: 5px; }}
    </style>
</head>
<body>
    <h1>模板加载错误</h1>
    <div class="error">
        <p>无法加载模板(ID: {template_id}): {str(e)}</p>
    </div>
</body>
</html>"""
            
            # 生成临时模板文件
            temp_template_path = self.template_base_path / "temp_preview.html"
            temp_config_path = self.config_base_path / "temp_preview.yaml"
            
            # 从config中获取HTML模板内容并保存
            config = template_data.get('config', {})
            print(f"配置数据类型: {type(config)}")
            
            if isinstance(config, str):
                try:
                    print("尝试解析JSON字符串配置")
                    config = json.loads(config)
                except json.JSONDecodeError as e:
                    print(f"JSON解析错误: {e}")
                    config = {}
            
            html_content = config.get('html_content', '')
            if not html_content:
                print("错误: 模板HTML内容为空")
                raise HTTPException(status_code=400, detail="模板HTML内容不能为空")
            
            print(f"HTML内容长度: {len(html_content)}")
            with open(temp_template_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            # 保存临时配置文件
            yaml_config = template_data.get('yaml_config', '')
            if not yaml_config:
                print("警告: YAML配置为空，使用默认值")
                yaml_config = '# 默认YAML配置\npaper_id: 1\npaper_name: "测试试卷"\npaper_description: "测试描述"\npaper_version: "v1.0"\n'
            
            print(f"YAML配置长度: {len(yaml_config)}")
            with open(temp_config_path, 'w', encoding='utf-8') as f:
                f.write(yaml_config)
                
            try:
                print("调用生成预览HTML函数")
                # 使用测试数据生成预览HTML
                from reports.generators.generate_report import generate_preview_html
                preview_html = generate_preview_html(
                    config_path=str(temp_config_path),
                    template_path=str(temp_template_path),
                    test_data=test_data
                )
                
                if not preview_html:
                    print("错误: 生成的预览HTML为空")
                    return "<!DOCTYPE html><html><body><h1>预览生成失败</h1><p>生成的HTML内容为空</p></body></html>"
                
                print(f"预览HTML生成成功，长度: {len(preview_html)}")
                return preview_html
            except Exception as e:
                import traceback
                print(f"生成预览HTML时出错: {str(e)}")
                print(traceback.format_exc())
                # 返回错误HTML而不是抛出异常
                return f"""<!DOCTYPE html>
<html>
<head>
    <title>预览生成错误</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .error {{ color: red; padding: 10px; border: 1px solid red; border-radius: 5px; }}
        pre {{ background: #f8f8f8; padding: 10px; overflow: auto; }}
    </style>
</head>
<body>
    <h1>预览生成错误</h1>
    <div class="error">
        <h2>错误信息:</h2>
        <p>{str(e)}</p>
    </div>
    <h3>可能的原因:</h3>
    <ul>
        <li>YAML配置格式错误</li>
        <li>HTML模板语法错误</li>
        <li>模板变量未定义</li>
    </ul>
    <p>请检查并修正配置后重试。</p>
</body>
</html>"""
        except Exception as e:
            import traceback
            print(f"生成预览过程中出错: {str(e)}")
            print(traceback.format_exc())
            raise HTTPException(status_code=500, detail=f"生成预览失败: {str(e)}")
        finally:
            # 删除临时文件
            try:
                if temp_template_path.exists():
                    temp_template_path.unlink()
                if temp_config_path.exists():
                    temp_config_path.unlink()
            except Exception as e:
                print(f"清理临时文件时出错: {str(e)}")
    
    def get_template_components(self, component_type: Optional[str] = None) -> Dict[str, Any]:
        """获取模板组件库"""
        if component_type:
            # 获取指定类型的组件
            return get_components_by_type(component_type)
        else:
            # 返回所有类型的组件
            return {
                "header": get_components_by_type("header"),
                "text": get_components_by_type("text"),
                "chart": get_components_by_type("chart"),
                "dimension": get_components_by_type("dimension"),
                "summary": get_components_by_type("summary"),
                "footer": get_components_by_type("footer")
            }
    
    def generate_template_from_components(self, components: List[Dict[str, str]]) -> str:
        """根据组件列表生成HTML模板"""
        return generate_template_with_components(components)
    
    def generate_default_template(self) -> str:
        """生成默认模板"""
        return generate_default_template()
    
    def _save_template_files(self, template: ReportTemplate) -> None:
        """保存模板文件到磁盘"""
        # 解析配置
        try:
            config = json.loads(template.config)
            yaml_config = template.yaml_config
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="配置JSON格式无效")
            
        # 保存YAML配置文件
        config_filename = f"{template.paper_id}.yaml"
        config_path = self.config_base_path / config_filename
        
        with open(config_path, 'w', encoding='utf-8') as f:
            f.write(yaml_config)
            
        # 保存HTML模板文件
        template_name = config.get('template', {}).get('name', 'default_template.html')
        template_path = self.template_base_path / template_name
        
        # 从配置中获取HTML内容
        html_content = config.get('html_content', '')
        
        if html_content:
            with open(template_path, 'w', encoding='utf-8') as f:
                f.write(html_content)

# 创建服务实例
report_template_service = ReportTemplateService() 
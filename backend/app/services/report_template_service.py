import os
import json
from pathlib import Path
from fastapi import HTTPException
import yaml
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional, List
from datetime import datetime

from app.models.report_template import ReportTemplate
from app.schemas.report_template import ReportTemplateCreate, ReportTemplateUpdate
from reports.generators.generate_report import generate_preview_html
from reports.generators.template_components import (
    get_component, get_components_by_type, 
    generate_template_with_components, generate_default_template
)

class ReportTemplateService:
    def __init__(self):
        # 获取当前文件所在目录
        current_dir = Path(__file__).parent.parent.parent
        
        # 设置正确的路径
        self.template_base_path = current_dir / "reports" / "generators" / "templates"
        self.template_base_path.mkdir(exist_ok=True, parents=True)
        self.config_base_path = current_dir / "reports" / "generators" / "configs"
        self.config_base_path.mkdir(exist_ok=True, parents=True)
        
        print(f"模板路径设置为: {self.template_base_path}")
        print(f"配置路径设置为: {self.config_base_path}")
        
        # 检查并迁移旧路径中的配置文件
        old_base_dir = current_dir / "backend"
        if old_base_dir.exists():
            old_config_path = old_base_dir / "reports" / "generators" / "configs"
            old_template_path = old_base_dir / "reports" / "generators" / "templates"
            self._migrate_files_if_needed(old_config_path, self.config_base_path)
            self._migrate_files_if_needed(old_template_path, self.template_base_path)
            
    def _migrate_files_if_needed(self, old_path: Path, new_path: Path):
        """将旧路径中的文件迁移到新路径
        
        Args:
            old_path: 旧的文件路径
            new_path: 新的文件路径
        """
        if old_path.exists():
            print(f"发现旧路径: {old_path}，迁移文件到: {new_path}")
            try:
                # 确保目标目录存在
                new_path.mkdir(exist_ok=True, parents=True)
                
                # 复制所有文件
                for file in old_path.glob('*.*'):
                    target_file = new_path / file.name
                    if not target_file.exists():
                        import shutil
                        shutil.copy2(file, target_file)
                        print(f"已复制文件: {file.name} 到 {target_file}")
                    else:
                        print(f"目标文件已存在，跳过: {target_file}")
            except Exception as e:
                print(f"迁移文件时出错: {str(e)}")

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
            
            # 确保config字段是字典，而不是JSON字符串
            if template.config and isinstance(template.config, str):
                try:
                    template.config = json.loads(template.config)
                except json.JSONDecodeError as e:
                    print(f"解析config JSON失败: {e}")
                    template.config = {}  # 解析失败时提供一个空字典
            
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
            
            # 获取HTML内容，如果不存在则使用默认模板
            html_content = config.get('html_content', '')
            if not html_content:
                print("警告: 模板HTML内容为空，使用默认模板")
                html_content = """<!DOCTYPE html>
<html>
<head>
    <title>测评报告预览</title>
    <meta charset="UTF-8">
    <style>
        body { 
            font-family: Arial, "Microsoft YaHei", sans-serif; 
            margin: 0; 
            padding: 0;
            color: #333;
            line-height: 1.6;
            background-color: #f9f9f9;
        }
        .container {
            max-width: 1000px;
            margin: 0 auto;
            background: white;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
            padding: 20px;
        }
        .header { 
            background: linear-gradient(135deg, #6b73ff 0%, #000dff 100%);
            color: white;
            padding: 30px;
            text-align: center;
            margin-bottom: 30px;
            border-radius: 5px;
        }
        .content { 
            padding: 20px;
        }
        .score-section {
            background-color: #f5f5f5;
            padding: 20px;
            border-radius: 5px;
            margin-bottom: 30px;
        }
        h1 { 
            margin: 0; 
            font-size: 28px;
        }
        h2 {
            color: #4a4a4a;
            border-left: 4px solid #000dff;
            padding-left: 10px;
            margin-top: 30px;
        }
        .score-card {
            display: flex;
            flex-wrap: wrap;
            gap: 20px;
            margin-top: 20px;
        }
        .dimension-card {
            flex: 1;
            min-width: 200px;
            background: white;
            border-radius: 5px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            padding: 15px;
            border-top: 3px solid #000dff;
        }
        .dimension-name {
            font-weight: bold;
            margin-bottom: 10px;
        }
        .dimension-score {
            font-size: 24px;
            color: #000dff;
            font-weight: bold;
        }
        .chart-section {
            margin: 30px 0;
            text-align: center;
        }
        .chart-image {
            max-width: 100%;
            height: auto;
        }
        .evaluation {
            background: white;
            border-radius: 5px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            padding: 20px;
            margin-bottom: 20px;
        }
        .footer {
            text-align: center;
            margin-top: 40px;
            font-size: 12px;
            color: #888;
            border-top: 1px solid #eee;
            padding-top: 20px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{{user_info.name}} 的测评报告</h1>
            <p>综合得分: {{user_info.total_score}}</p>
        </div>
        
        <div class="content">
            <div class="score-section">
                <h2>维度评分概览</h2>
                <div class="score-card">
                    {% for dim_name, dim in dimensions.items() %}
                    <div class="dimension-card">
                        <div class="dimension-name">{{dim_name}}</div>
                        <div class="dimension-score">{{dim.score}}</div>
                    </div>
                    {% endfor %}
                </div>
            </div>
            
            <div class="chart-section">
                <h2>能力雷达图</h2>
                <img class="chart-image" src="{{chart_img}}" alt="能力雷达图">
            </div>
            
            <h2>综合评价</h2>
            <div class="evaluation">
                <p>{{performance_eval.summary}}</p>
            </div>
            
            <h2>发展建议</h2>
            <div class="evaluation">
                <p>{{performance_eval.development_focus}}</p>
            </div>
            
            <div class="footer">
                <p>此报告由智能评测系统生成 {{ '&copy;' }} {{now.year}} 测评系统</p>
            </div>
        </div>
    </div>
</body>
</html>"""
            
            print(f"HTML内容长度: {len(html_content)}")
            print(f"HTML内容预览: {html_content[:100]}..." if len(html_content) > 100 else html_content)
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
            
            # 创建测试数据（默认值）
            if test_data is None:
                # 创建预览用的测试数据，确保dimensions是字典而不是列表
                test_data = {
                    "user_info": {
                        "name": "测试用户",
                        "total_score": 7.8,
                        "department": "产品部",
                        "position": "产品经理",
                        "test_date": datetime.now().strftime("%Y-%m-%d")
                    },
                    "dimensions": {
                        "学习能力": {"score": 8.5, "subs": {"学习动机": 8.7, "信息获取": 8.3, "知识应用": 8.5}},
                        "沟通协作": {"score": 7.2, "subs": {"表达能力": 7.5, "倾听能力": 6.9, "团队合作": 7.2}},
                        "创新思维": {"score": 8.1, "subs": {"发散思维": 8.3, "问题解决": 7.9, "创新实践": 8.1}},
                        "执行力": {"score": 7.6, "subs": {"计划制定": 7.8, "行动效率": 7.4, "结果导向": 7.6}}
                    },
                    "performance_eval": {
                        "summary": "该候选人整体表现良好，展现出较强的学习能力和创新思维。学习能力方面表现突出，善于获取信息并灵活应用知识，能够快速适应新环境和新任务的要求。创新思维富有活力，能提出有创意的解决方案。沟通协作与执行力表现稳定，但在倾听能力方面仍有提升空间。",
                        "development_focus": "建议重点提升沟通中的倾听能力，加强与团队成员的互动与反馈；同时可进一步强化执行过程中的效率管理，建立更清晰的工作优先级，确保在保证质量的前提下提高整体执行效率。"
                    },
                    "strengths": {
                        "学习能力": {"score": 8.5, "details": "学习吸收新知识快，善于将理论应用到实践中"},
                        "创新思维": {"score": 8.1, "details": "能够提出创新性解决方案，思考问题有独特视角"}
                    },
                    "weaknesses": {
                        "倾听能力": {"score": 6.9, "details": "在团队讨论中有时倾向于表达而非倾听"},
                        "行动效率": {"score": 7.4, "details": "在压力下工作效率有所波动"}
                    },
                    "chart_img": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="
                }
                
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
    <h3>错误堆栈:</h3>
    <pre>{traceback.format_exc()}</pre>
    <h3>可能的原因:</h3>
    <ul>
        <li>YAML配置格式错误</li>
        <li>HTML模板语法错误</li>
        <li>模板变量未定义</li>
    </ul>
    <p>请检查配置和模板是否正确。</p>
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
    
    # 添加设计器模板相关方法
    def create_designer_template(self, db: Session, template_data: Dict[str, Any]) -> ReportTemplate:
        """创建新的设计器模板
        
        Args:
            db: 数据库会话
            template_data: 模板数据，包含name、components和html_content
            
        Returns:
            创建的模板对象
        """
        name = template_data.get('name')
        if not name:
            raise ValueError("模板名称不能为空")
            
        # 将组件列表和HTML内容保存到config字段
        config = {
            'components': template_data.get('components', []),
            'html_content': template_data.get('html_content', ''),
            'template_type': 'designer'  # 标记为设计器模板
        }
        
        # 创建模板记录
        db_template = ReportTemplate(
            name=name,
            paper_id=template_data.get('paper_id', 0),  # 默认使用0作为paper_id表示这是设计器模板
            config=json.dumps(config, ensure_ascii=False),
            yaml_config="template_type: designer\n"  # 简单的YAML配置，标记类型
        )
        
        db.add(db_template)
        db.commit()
        db.refresh(db_template)
        
        return db_template
    
    def get_designer_templates(self, db: Session) -> List[ReportTemplate]:
        """获取设计器模板列表
        
        Args:
            db: 数据库会话
            
        Returns:
            设计器模板列表
        """
        # 使用paper_id=0或通过配置中的template_type字段筛选设计器模板
        templates = db.query(ReportTemplate).filter(ReportTemplate.paper_id == 0).all()
        return templates
    
    def get_designer_template(self, db: Session, template_id: int) -> Optional[ReportTemplate]:
        """获取单个设计器模板详情
        
        Args:
            db: 数据库会话
            template_id: 模板ID
            
        Returns:
            设计器模板对象或None
        """
        template = db.query(ReportTemplate).filter(ReportTemplate.id == template_id).first()
        return template
    
    def delete_designer_template(self, db: Session, template_id: int) -> bool:
        """删除设计器模板
        
        Args:
            db: 数据库会话
            template_id: 模板ID
            
        Returns:
            是否成功删除
        """
        template = self.get_designer_template(db, template_id)
        if not template:
            return False
        
        db.delete(template)
        db.commit()
        return True

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
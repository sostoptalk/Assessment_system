"""
报告模板组件库

提供预定义的模板组件，用于在前端快速构建报告模板
"""

# 默认组件
DEFAULT_COMPONENTS = {
    # 页眉组件
    "header": {
        "simple": {
            "name": "简单页眉",
            "description": "显示标题和基本用户信息",
            "html": """
<!-- component:header id:simple_header -->
<header style="text-align: center; margin-bottom: 20px; padding: 10px; border-bottom: 2px solid #3498db;">
    <h1 style="color: #2c3e50; margin: 5px 0;">{{ report_title|default('测评报告') }}</h1>
    <p><strong>姓名：</strong>{{ user_info.name }}</p>
    <p><strong>测评日期：</strong>{{ current_date|default('2025年5月') }}</p>
</header>
<!-- /component -->
"""
        },
        "professional": {
            "name": "专业页眉",
            "description": "带logo的企业风格页眉",
            "html": """
<!-- component:header id:professional_header -->
<header style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; padding: 15px; border-bottom: 3px solid #2c3e50; background: linear-gradient(to right, #f5f7fa, #ffffff);">
    <div style="text-align: left;">
        <h1 style="color: #2c3e50; margin: 0; font-size: 24px;">{{ report_title|default('专业测评报告') }}</h1>
        <p style="color: #7f8c8d; margin: 5px 0 0 0; font-size: 14px;">{{ subtitle|default('全面分析与发展建议') }}</p>
    </div>
    <div style="text-align: right;">
        <p style="margin: 0;"><strong>{{ user_info.name }}</strong></p>
        <p style="margin: 5px 0 0 0; font-size: 12px; color: #7f8c8d;">{{ current_date|default('2025年5月') }}</p>
    </div>
</header>
<!-- /component -->
"""
        }
    },
    
    # 文本段落组件
    "text": {
        "simple_paragraph": {
            "name": "简单段落",
            "description": "基本文本段落",
            "html": """
<!-- component:text id:simple_paragraph -->
<div style="margin: 15px 0; line-height: 1.6;">
    <p>{{ paragraph_text|default('在这里输入段落内容，可以包含对测评结果的分析和解释。') }}</p>
</div>
<!-- /component -->
"""
        },
        "highlighted": {
            "name": "强调段落",
            "description": "带有强调样式的文本段落",
            "html": """
<!-- component:text id:highlighted_paragraph -->
<div style="margin: 15px 0; padding: 15px; background-color: #f8f9fa; border-left: 4px solid #3498db; border-radius: 0 5px 5px 0;">
    <p style="margin: 0; line-height: 1.6;"><strong>{{ title|default('重点说明') }}：</strong>{{ content|default('这里是需要强调的重要内容，将以醒目的样式呈现。') }}</p>
</div>
<!-- /component -->
"""
        },
        "reading_guide": {
            "name": "阅读指南",
            "description": "报告阅读说明",
            "html": """
<!-- component:text id:reading_guide -->
<div style="margin: 20px 0; padding: 20px; background: linear-gradient(135deg, #f5f9ff, #e8f4ff); border-radius: 8px; border: 1px solid #d9e9ff;">
    <h3 style="color: #2c3e50; margin-top: 0;">阅读指南</h3>
    <p>{{ guide_content|default('本报告基于标准化测评结果生成，旨在提供个人能力特点的客观描述和发展建议。报告中的分数和评价是相对于参考群体的，无优劣之分，请结合实际情况参考。') }}</p>
    <div style="margin-top: 15px;">
        <strong>分数说明：</strong>
        <ul style="margin-top: 5px;">
            <li>8.5-10分：表现优秀</li>
            <li>7.5-8.4分：表现良好</li>
            <li>6.5-7.4分：表现一般</li>
            <li>6.4分以下：有待提升</li>
        </ul>
    </div>
</div>
<!-- /component -->
"""
        }
    },
    
    # 图表组件
    "chart": {
        "radar": {
            "name": "雷达图",
            "description": "显示各维度能力分布的雷达图",
            "html": """
<!-- component:chart id:radar_chart -->
<div style="margin: 20px 0; text-align: center;">
    <h3 style="color: #2c3e50; margin-bottom: 10px;">{{ chart_title|default('能力维度分布') }}</h3>
    <div style="border: 1px solid #eee; border-radius: 5px; padding: 10px; background-color: #fff;">
        <img src="{{ chart_img }}" alt="维度分析图" style="max-width: 100%; height: auto;">
    </div>
    <p style="font-style: italic; color: #7f8c8d; font-size: 12px; margin-top: 5px;">{{ chart_description|default('上图展示了各维度的相对得分分布') }}</p>
</div>
<!-- /component -->
"""
        }
    },
    
    # 维度展示组件
    "dimension": {
        "simple": {
            "name": "简单维度展示",
            "description": "简洁地显示维度得分和评价",
            "html": """
<!-- component:dimension id:simple_dimension -->
<div style="margin: 20px 0;">
    <h3 style="color: #2c3e50; margin-bottom: 15px; border-bottom: 1px solid #ecf0f1; padding-bottom: 8px;">维度详细分析</h3>
    
    {% for dim in dimensions %}
    <div style="margin: 15px 0; padding: 15px; background-color: #f8f9fa; border-radius: 5px; border-left: 4px solid #3498db;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
            <h4 style="margin: 0; color: #2c3e50;">{{ dim.name }}</h4>
            <span style="font-weight: bold; color: #3498db;">{{ dim.score|round(1) }} 分</span>
        </div>
        
        {% if dimension_evaluations[dim.name] %}
        <p style="margin: 10px 0; font-style: italic;">{{ dimension_evaluations[dim.name].dimension_eval }}</p>
        {% endif %}
    </div>
    {% endfor %}
</div>
<!-- /component -->
"""
        },
        "detailed": {
            "name": "详细维度展示",
            "description": "显示维度和子维度的得分和评价",
            "html": """
<!-- component:dimension id:detailed_dimension -->
<div style="margin: 20px 0;">
    <h3 style="color: #2c3e50; margin-bottom: 15px; border-bottom: 1px solid #ecf0f1; padding-bottom: 8px;">维度详细分析</h3>
    
    {% for dim in dimensions %}
    <div style="margin: 20px 0; padding: 20px; background-color: #f8f9fa; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; border-bottom: 1px solid #ecf0f1; padding-bottom: 10px;">
            <h4 style="margin: 0; color: #2c3e50;">{{ dim.name }}</h4>
            <div>
                <span style="font-weight: bold; font-size: 16px; color: #3498db;">{{ dim.score|round(1) }} 分</span>
                
                {% if dimension_evaluations[dim.name] %}
                <span style="margin-left: 10px; padding: 3px 10px; border-radius: 20px; background-color: 
                {% if dimension_evaluations[dim.name].eval_level == 'high' %}#27ae60{% elif dimension_evaluations[dim.name].eval_level == 'medium' %}#f39c12{% else %}#e74c3c{% endif %}; 
                color: white; font-size: 12px;">
                {% if dimension_evaluations[dim.name].eval_level == 'high' %}优秀{% elif dimension_evaluations[dim.name].eval_level == 'medium' %}良好{% else %}待提升{% endif %}
                </span>
                {% endif %}
            </div>
        </div>
        
        {% if dimension_evaluations[dim.name] %}
        <div style="margin-bottom: 15px; padding: 10px; background-color: #ebf5fb; border-radius: 5px;">
            <p style="margin: 0;">{{ dimension_evaluations[dim.name].dimension_eval }}</p>
        </div>
        {% endif %}
        
        <!-- 子维度展示 -->
        {% if dim.subs and dim.subs|length > 0 %}
        <div style="margin-top: 15px;">
            <h5 style="color: #7f8c8d; margin-bottom: 10px;">子维度分析</h5>
            
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 15px;">
                {% for sub_name, sub_data in dim.subs.items() %}
                <div style="padding: 15px; background-color: white; border-radius: 5px; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                        <span style="font-weight: bold;">{{ sub_name }}</span>
                        <span style="color: #3498db; font-weight: bold;">{{ sub_data.score|round(1) }}分</span>
                    </div>
                    
                    {% if sub_data.evaluation %}
                    <div style="font-size: 13px; color: #555;">
                        <p style="margin: 5px 0;"><strong>特点：</strong>{{ sub_data.evaluation.潜质特点 }}</p>
                        <p style="margin: 5px 0;"><strong>工作表现：</strong>{{ sub_data.evaluation.工作中的倾向 }}</p>
                    </div>
                    {% endif %}
                </div>
                {% endfor %}
            </div>
        </div>
        {% endif %}
    </div>
    {% endfor %}
</div>
<!-- /component -->
"""
        }
    },
    
    # 总结组件
    "summary": {
        "simple": {
            "name": "简单总结",
            "description": "简洁的报告总结",
            "html": """
<!-- component:summary id:simple_summary -->
<div style="margin: 20px 0; padding: 20px; background-color: #f9f9f9; border-radius: 5px; border: 1px solid #eee;">
    <h3 style="color: #2c3e50; margin-top: 0;">总结与建议</h3>
    
    <div style="margin-top: 15px;">
        <h4 style="color: #3498db; margin-bottom: 10px;">总体评价</h4>
        <p>{{ performance_eval.summary }}</p>
    </div>
    
    <div style="margin-top: 15px;">
        <h4 style="color: #3498db; margin-bottom: 10px;">发展建议</h4>
        <p>{{ performance_eval.development_focus }}</p>
    </div>
</div>
<!-- /component -->
"""
        },
        "detailed": {
            "name": "详细总结",
            "description": "包含优劣势分析的详细总结",
            "html": """
<!-- component:summary id:detailed_summary -->
<div style="margin: 20px 0; padding: 20px; background-color: #f5f9ff; border-radius: 8px; border: 1px solid #d4e6f1;">
    <h3 style="color: #2c3e50; margin-top: 0; border-bottom: 2px solid #3498db; padding-bottom: 10px;">总结与发展建议</h3>
    
    <div style="display: flex; gap: 20px; margin-top: 20px;">
        <!-- 优势分析 -->
        <div style="flex: 1; background-color: #eafaf1; padding: 15px; border-radius: 5px; border-left: 4px solid #27ae60;">
            <h4 style="color: #27ae60; margin-top: 0;">优势领域</h4>
            {% if strengths|get_dim_strengths or strengths|get_sub_strengths %}
            <ul style="padding-left: 20px;">
                {% for item in strengths|get_dim_strengths %}
                <li><strong>{{ item.name }}</strong>: {{ item.score|round(2) }}分
                    (高于平均 {{ (item.score - item.average)|round(2) }}分)
                </li>
                {% endfor %}

                {% for item in strengths|get_sub_strengths %}
                <li><em>{{ item.name }}</em>: {{ item.score|round(2) }}分
                    (高于平均 {{ (item.score - item.average)|round(2) }}分)
                </li>
                {% endfor %}
            </ul>
            {% else %}
            <p>未检测到显著优势领域</p>
            {% endif %}
        </div>
        
        <!-- 待提升领域 -->
        <div style="flex: 1; background-color: #fdedec; padding: 15px; border-radius: 5px; border-left: 4px solid #e74c3c;">
            <h4 style="color: #e74c3c; margin-top: 0;">发展领域</h4>
            {% if weaknesses|get_dim_weaknesses or weaknesses|get_sub_weaknesses %}
            <ul style="padding-left: 20px;">
                {% for item in weaknesses|get_dim_weaknesses %}
                <li><strong>{{ item.name }}</strong>: {{ item.score|round(2) }}分
                    (低于平均 {{ (item.average - item.score)|round(2) }}分)
                </li>
                {% endfor %}

                {% for item in weaknesses|get_sub_weaknesses %}
                <li><em>{{ item.name }}</em>: {{ item.score|round(2) }}分
                    (低于平均 {{ (item.average - item.score)|round(2) }}分)
                </li>
                {% endfor %}
            </ul>
            {% else %}
            <p>未检测到显著发展领域</p>
            {% endif %}
        </div>
    </div>
    
    <!-- 发展建议 -->
    <div style="margin-top: 20px; background-color: white; padding: 15px; border-radius: 5px; border: 1px solid #eee;">
        <h4 style="color: #3498db; margin-top: 0;">个性化发展建议</h4>
        
        <p>{{ performance_eval.development_focus }}</p>
        
        {% set top_strength = strengths|get_top_strength %}
        {% set main_weakness = weaknesses|get_main_weakness %}
        
        <ul style="margin-top: 15px;">
            {% if top_strength %}
            <li style="margin-bottom: 10px;"><strong>优势强化</strong>：继续发挥{{ top_strength.name }}领域的优势，进一步提升专业深度</li>
            {% endif %}
            
            {% if main_weakness %}
            <li style="margin-bottom: 10px;"><strong>重点发展</strong>：针对{{ main_weakness.name }}领域，建议参加相关培训和实践项目</li>
            {% endif %}
            
            <li style="margin-bottom: 10px;"><strong>持续学习</strong>：建立个人发展计划，持续关注行业前沿知识和技能</li>
        </ul>
    </div>
</div>
<!-- /component -->
"""
        }
    },
    
    # 页脚组件
    "footer": {
        "simple": {
            "name": "简单页脚",
            "description": "简单的页脚信息",
            "html": """
<!-- component:footer id:simple_footer -->
<footer style="margin-top: 30px; padding-top: 15px; border-top: 1px solid #ecf0f1; text-align: center; color: #7f8c8d; font-size: 12px;">
    <p>本报告由专业测评系统生成，内容仅作参考</p>
    <p>© {{ current_year|default('2025') }} 人力资源部 | 保密文件</p>
</footer>
<!-- /component -->
"""
        }
    }
}

# 获取某类型的所有组件
def get_components_by_type(component_type):
    """获取指定类型的所有组件
    
    Args:
        component_type: 组件类型
        
    Returns:
        该类型的所有组件字典
    """
    return DEFAULT_COMPONENTS.get(component_type, {})

# 获取指定组件
def get_component(component_type, component_id):
    """获取指定类型和ID的组件
    
    Args:
        component_type: 组件类型
        component_id: 组件ID
        
    Returns:
        组件信息或None
    """
    components = DEFAULT_COMPONENTS.get(component_type, {})
    return components.get(component_id)

# 生成带组件的HTML模板
def generate_template_with_components(components_list):
    """根据组件列表生成完整HTML模板
    
    Args:
        components_list: 组件列表，包含类型和ID
        
    Returns:
        完整的HTML模板字符串
    """
    template = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>测评报告</title>
    <style>
        * {
            box-sizing: border-box;
            font-family: 'Microsoft YaHei', 'SimHei', sans-serif;
            margin: 0;
            padding: 0;
        }
        
        body {
            margin: 0 auto;
            padding: 20px;
            max-width: 800px;
            line-height: 1.5;
            color: #333;
            background-color: #fff;
        }
    </style>
</head>
<body>
"""
    
    # 添加组件
    for comp in components_list:
        comp_type = comp.get('type')
        comp_id = comp.get('id')
        
        component = get_component(comp_type, comp_id)
        if component:
            template += "\n" + component['html'] + "\n"
    
    # 结束HTML
    template += """
</body>
</html>
"""
    return template

# 生成默认模板
def generate_default_template():
    """生成默认报告模板
    
    Returns:
        默认模板字符串
    """
    try:
        print("开始生成默认模板...")
        components = [
            {'type': 'header', 'id': 'simple'},
            {'type': 'text', 'id': 'reading_guide'},
            {'type': 'chart', 'id': 'radar'},
            {'type': 'dimension', 'id': 'detailed'},
            {'type': 'summary', 'id': 'simple'},
            {'type': 'footer', 'id': 'simple'}
        ]
        
        print("使用预定义组件生成模板...")
        template = generate_template_with_components(components)
        
        if not isinstance(template, str):
            print(f"错误: 生成的模板不是字符串类型，而是 {type(template)}")
            # 转换为字符串
            template = str(template)
        
        print(f"模板生成成功，内容长度: {len(template)}")
        return template
    except Exception as e:
        import traceback
        print(f"生成默认模板时出错: {str(e)}")
        print(traceback.format_exc())
        # 如果出错，返回最小化的可用模板
        minimal_template = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>测评报告</title>
</head>
<body>
    <h1>测评报告模板</h1>
    <p>请添加模板组件构建您的报告模板</p>
</body>
</html>"""
        print("返回最小化模板")
        return minimal_template 
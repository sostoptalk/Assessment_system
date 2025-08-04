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
    },

    # 添加新的表格组件类型
    "table": {
        "basic_table": {
            "name": "基本表格",
            "description": "简单的维度得分表格",
            "html": """
<!-- component:table id:basic_table -->
<div style="margin: 20px 0;">
    <h3 style="color: #2c3e50; margin-bottom: 15px;">{{ table_title|default('维度得分表') }}</h3>
    <table style="width: 100%; border-collapse: collapse; border: 1px solid #e0e0e0;">
        <thead>
            <tr style="background-color: #f2f6fa;">
                <th style="padding: 10px; text-align: left; border: 1px solid #e0e0e0;">维度</th>
                <th style="padding: 10px; text-align: center; border: 1px solid #e0e0e0;">得分</th>
                <th style="padding: 10px; text-align: center; border: 1px solid #e0e0e0;">评级</th>
            </tr>
        </thead>
        <tbody>
            {% for dim in dimensions %}
            <tr>
                <td style="padding: 10px; border: 1px solid #e0e0e0;">{{ dim.name }}</td>
                <td style="padding: 10px; text-align: center; border: 1px solid #e0e0e0; font-weight: bold; color: #3498db;">{{ dim.score|round(1) }}</td>
                <td style="padding: 10px; text-align: center; border: 1px solid #e0e0e0;">
                    {% if dim.score >= 8.5 %}
                    <span style="color: #27ae60;">优秀</span>
                    {% elif dim.score >= 7.5 %}
                    <span style="color: #3498db;">良好</span>
                    {% elif dim.score >= 6.5 %}
                    <span style="color: #f39c12;">一般</span>
                    {% else %}
                    <span style="color: #e74c3c;">待提升</span>
                    {% endif %}
                </td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
</div>
<!-- /component -->
"""
        },
        "detailed_table": {
            "name": "详细表格",
            "description": "带子维度的详细得分表格",
            "html": """
<!-- component:table id:detailed_table -->
<div style="margin: 20px 0;">
    <h3 style="color: #2c3e50; margin-bottom: 15px;">{{ table_title|default('维度得分详情表') }}</h3>
    <table style="width: 100%; border-collapse: collapse; border: 1px solid #e0e0e0;">
        <thead>
            <tr style="background-color: #f2f6fa;">
                <th style="padding: 10px; text-align: left; border: 1px solid #e0e0e0;">维度/子维度</th>
                <th style="padding: 10px; text-align: center; border: 1px solid #e0e0e0;">得分</th>
                <th style="padding: 10px; text-align: center; border: 1px solid #e0e0e0;">评级</th>
                <th style="padding: 10px; text-align: left; border: 1px solid #e0e0e0;">描述</th>
            </tr>
        </thead>
        <tbody>
            {% for dim in dimensions %}
            <tr style="background-color: #f9f9f9;">
                <td style="padding: 10px; border: 1px solid #e0e0e0; font-weight: bold;">{{ dim.name }}</td>
                <td style="padding: 10px; text-align: center; border: 1px solid #e0e0e0; font-weight: bold; color: #3498db;">{{ dim.score|round(1) }}</td>
                <td style="padding: 10px; text-align: center; border: 1px solid #e0e0e0;">
                    {% if dim.score >= 8.5 %}
                    <span style="color: #27ae60;">优秀</span>
                    {% elif dim.score >= 7.5 %}
                    <span style="color: #3498db;">良好</span>
                    {% elif dim.score >= 6.5 %}
                    <span style="color: #f39c12;">一般</span>
                    {% else %}
                    <span style="color: #e74c3c;">待提升</span>
                    {% endif %}
                </td>
                <td style="padding: 10px; border: 1px solid #e0e0e0;">
                    {% if dimension_evaluations[dim.name] %}
                    {{ dimension_evaluations[dim.name].dimension_eval|truncate(60) }}
                    {% endif %}
                </td>
            </tr>
            {% if dim.subs %}
                {% for sub_name, sub_data in dim.subs.items() %}
                <tr>
                    <td style="padding: 10px; padding-left: 30px; border: 1px solid #e0e0e0; font-style: italic;">{{ sub_name }}</td>
                    <td style="padding: 10px; text-align: center; border: 1px solid #e0e0e0; color: #3498db;">{{ sub_data.score|round(1) }}</td>
                    <td style="padding: 10px; text-align: center; border: 1px solid #e0e0e0;">
                        {% if sub_data.score >= 8.5 %}
                        <span style="color: #27ae60;">优秀</span>
                        {% elif sub_data.score >= 7.5 %}
                        <span style="color: #3498db;">良好</span>
                        {% elif sub_data.score >= 6.5 %}
                        <span style="color: #f39c12;">一般</span>
                        {% else %}
                        <span style="color: #e74c3c;">待提升</span>
                        {% endif %}
                    </td>
                    <td style="padding: 10px; border: 1px solid #e0e0e0; font-size: 0.9em;">
                        {% if sub_data.evaluation %}
                        {{ sub_data.evaluation.潜质特点|truncate(50) }}
                        {% endif %}
                    </td>
                </tr>
                {% endfor %}
            {% endif %}
            {% endfor %}
        </tbody>
    </table>
</div>
<!-- /component -->
"""
        }
    },

    # 添加新的评分卡组件类型
    "scorecard": {
        "modern": {
            "name": "现代评分卡",
            "description": "现代风格的评分卡",
            "html": """
<!-- component:scorecard id:modern_scorecard -->
<div style="margin: 20px 0; padding: 20px; background-color: #f9f9f9; border-radius: 8px;">
    <h3 style="color: #2c3e50; margin-bottom: 15px; border-bottom: 2px solid #3498db; padding-bottom: 10px;">{{ scorecard_title|default('测评结果评分卡') }}</h3>
    
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
        <div>
            <h4 style="margin: 0; color: #2c3e50;">{{ user_info.name }}</h4>
            <p style="margin: 5px 0 0 0; color: #7f8c8d;">{{ user_info.department }} / {{ user_info.position }}</p>
        </div>
        <div style="text-align: right;">
            <div style="font-size: 24px; font-weight: bold; color: 
            {% if user_info.total_score >= 8.5 %}#27ae60
            {% elif user_info.total_score >= 7.5 %}#3498db
            {% elif user_info.total_score >= 6.5 %}#f39c12
            {% else %}#e74c3c{% endif %};">
                {{ user_info.total_score|round(1) }}
            </div>
            <div style="color: #7f8c8d;">总分</div>
        </div>
    </div>
    
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 15px; margin-top: 20px;">
        {% for dim in dimensions %}
        <div style="padding: 15px; background-color: white; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div style="font-weight: bold; color: #2c3e50;">{{ dim.name }}</div>
                <div style="font-size: 18px; font-weight: bold; color: 
                {% if dim.score >= 8.5 %}#27ae60
                {% elif dim.score >= 7.5 %}#3498db
                {% elif dim.score >= 6.5 %}#f39c12
                {% else %}#e74c3c{% endif %};">
                    {{ dim.score|round(1) }}
                </div>
            </div>
            
            <div style="margin-top: 10px;">
                <div style="height: 6px; background-color: #f1f1f1; border-radius: 3px; overflow: hidden;">
                    <div style="height: 100%; width: {{ (dim.score / 10) * 100 }}%; background: 
                    {% if dim.score >= 8.5 %}#27ae60
                    {% elif dim.score >= 7.5 %}#3498db
                    {% elif dim.score >= 6.5 %}#f39c12
                    {% else %}#e74c3c{% endif %};"></div>
                </div>
                <div style="display: flex; justify-content: space-between; margin-top: 5px; font-size: 12px; color: #7f8c8d;">
                    <span>0</span>
                    <span>5</span>
                    <span>10</span>
                </div>
            </div>
        </div>
        {% endfor %}
    </div>
</div>
<!-- /component -->
"""
        },
        "comparison": {
            "name": "对比评分卡",
            "description": "带对比功能的评分卡",
            "html": """
<!-- component:scorecard id:comparison_scorecard -->
<div style="margin: 20px 0; padding: 20px; background-color: #f9f9f9; border-radius: 8px;">
    <h3 style="color: #2c3e50; margin-bottom: 15px; border-bottom: 2px solid #3498db; padding-bottom: 10px;">{{ scorecard_title|default('能力对比评分卡') }}</h3>
    
    <div style="margin-bottom: 20px;">
        <div style="display: flex; margin-bottom: 5px; align-items: center;">
            <span style="width: 30%; font-weight: bold;">维度</span>
            <span style="width: 40%;">能力水平</span>
            <span style="width: 15%; text-align: center;">个人</span>
            <span style="width: 15%; text-align: center; color: #7f8c8d;">平均</span>
        </div>
        
        {% for dim in dimensions %}
        <div style="margin-bottom: 15px; padding-bottom: 15px; border-bottom: 1px solid #eee;">
            <div style="display: flex; margin-bottom: 5px; align-items: center;">
                <span style="width: 30%; font-weight: bold;">{{ dim.name }}</span>
                <div style="width: 40%; position: relative; height: 20px; background-color: #f1f1f1; border-radius: 10px;">
                    <!-- 平均值标记 -->
                    <div style="position: absolute; left: {{ (7 / 10) * 100 }}%; top: 0; bottom: 0; width: 2px; background-color: #95a5a6;"></div>
                    <!-- 得分进度条 -->
                    <div style="position: absolute; left: 0; top: 0; bottom: 0; width: {{ (dim.score / 10) * 100 }}%; background: 
                    {% if dim.score >= 8.5 %}#27ae60
                    {% elif dim.score >= 7.5 %}#3498db
                    {% elif dim.score >= 6.5 %}#f39c12
                    {% else %}#e74c3c{% endif %}; 
                    border-radius: 10px;"></div>
                </div>
                <span style="width: 15%; text-align: center; font-weight: bold; color:
                {% if dim.score >= 8.5 %}#27ae60
                {% elif dim.score >= 7.5 %}#3498db
                {% elif dim.score >= 6.5 %}#f39c12
                {% else %}#e74c3c{% endif %};">
                    {{ dim.score|round(1) }}
                </span>
                <span style="width: 15%; text-align: center; color: #7f8c8d;">7.0</span>
            </div>
            
            <!-- 子维度展示 -->
            {% if dim.subs %}
            <div style="margin-left: 30px;">
                {% for sub_name, sub_data in dim.subs.items() %}
                <div style="display: flex; margin-top: 8px; align-items: center; font-size: 0.9em;">
                    <span style="width: 30%; color: #7f8c8d;">{{ sub_name }}</span>
                    <div style="width: 40%; position: relative; height: 15px; background-color: #f1f1f1; border-radius: 7px;">
                        <!-- 平均值标记 -->
                        <div style="position: absolute; left: {{ (7 / 10) * 100 }}%; top: 0; bottom: 0; width: 2px; background-color: #95a5a6;"></div>
                        <!-- 得分进度条 -->
                        <div style="position: absolute; left: 0; top: 0; bottom: 0; width: {{ (sub_data.score / 10) * 100 }}%; background: 
                        {% if sub_data.score >= 8.5 %}#27ae60
                        {% elif sub_data.score >= 7.5 %}#3498db
                        {% elif sub_data.score >= 6.5 %}#f39c12
                        {% else %}#e74c3c{% endif %}; 
                        border-radius: 7px;"></div>
                    </div>
                    <span style="width: 15%; text-align: center; color:
                    {% if sub_data.score >= 8.5 %}#27ae60
                    {% elif sub_data.score >= 7.5 %}#3498db
                    {% elif sub_data.score >= 6.5 %}#f39c12
                    {% else %}#e74c3c{% endif %};">
                        {{ sub_data.score|round(1) }}
                    </span>
                    <span style="width: 15%; text-align: center; color: #7f8c8d;">7.0</span>
                </div>
                {% endfor %}
            </div>
            {% endif %}
        </div>
        {% endfor %}
    </div>
    
    <div style="font-size: 12px; color: #7f8c8d; text-align: right; margin-top: 10px;">
        注：平均值基于同级别/同岗位人员的历史数据
    </div>
</div>
<!-- /component -->
"""
        }
    },

    # 添加新的个人信息卡组件
    "profile": {
        "simple": {
            "name": "简洁个人信息",
            "description": "简洁的个人信息卡片",
            "html": """
<!-- component:profile id:simple_profile -->
<div style="margin: 20px 0; padding: 15px; background-color: #f8f9fa; border-radius: 5px; border: 1px solid #e9ecef;">
    <table style="width: 100%; border-collapse: collapse;">
        <tr>
            <td style="width: 20%; padding: 8px; color: #6c757d;">姓名</td>
            <td style="width: 30%; padding: 8px; font-weight: bold;">{{ user_info.name }}</td>
            <td style="width: 20%; padding: 8px; color: #6c757d;">部门</td>
            <td style="width: 30%; padding: 8px;">{{ user_info.department }}</td>
        </tr>
        <tr>
            <td style="padding: 8px; color: #6c757d;">职位</td>
            <td style="padding: 8px;">{{ user_info.position }}</td>
            <td style="padding: 8px; color: #6c757d;">测评日期</td>
            <td style="padding: 8px;">{{ user_info.test_date }}</td>
        </tr>
    </table>
</div>
<!-- /component -->
"""
        },
        "detailed": {
            "name": "详细个人信息",
            "description": "包含更多字段的个人信息展示",
            "html": """
<!-- component:profile id:detailed_profile -->
<div style="margin: 20px 0; padding: 20px; background-color: #f8f9fa; border-radius: 8px; border: 1px solid #e9ecef;">
    <h3 style="color: #2c3e50; margin-top: 0; margin-bottom: 15px; border-bottom: 1px solid #dee2e6; padding-bottom: 10px;">{{ profile_title|default('个人信息') }}</h3>
    
    <div style="display: flex; flex-wrap: wrap;">
        <div style="flex: 1; min-width: 300px; padding: 10px;">
            <table style="width: 100%; border-collapse: collapse;">
                <tr>
                    <td style="width: 30%; padding: 8px; color: #6c757d; vertical-align: top;">姓名</td>
                    <td style="padding: 8px; font-weight: bold;">{{ user_info.name }}</td>
                </tr>
                <tr>
                    <td style="padding: 8px; color: #6c757d; vertical-align: top;">部门</td>
                    <td style="padding: 8px;">{{ user_info.department }}</td>
                </tr>
                <tr>
                    <td style="padding: 8px; color: #6c757d; vertical-align: top;">职位</td>
                    <td style="padding: 8px;">{{ user_info.position }}</td>
                </tr>
                <tr>
                    <td style="padding: 8px; color: #6c757d; vertical-align: top;">工作年限</td>
                    <td style="padding: 8px;">{{ user_info.work_years|default('--') }}</td>
                </tr>
            </table>
        </div>
        
        <div style="flex: 1; min-width: 300px; padding: 10px;">
            <table style="width: 100%; border-collapse: collapse;">
                <tr>
                    <td style="width: 30%; padding: 8px; color: #6c757d; vertical-align: top;">测评名称</td>
                    <td style="padding: 8px;">{{ paper_name|default('综合能力测评') }}</td>
                </tr>
                <tr>
                    <td style="padding: 8px; color: #6c757d; vertical-align: top;">测评日期</td>
                    <td style="padding: 8px;">{{ user_info.test_date }}</td>
                </tr>
                <tr>
                    <td style="padding: 8px; color: #6c757d; vertical-align: top;">报告编号</td>
                    <td style="padding: 8px;">{{ report_id|default('--') }}</td>
                </tr>
                <tr>
                    <td style="padding: 8px; color: #6c757d; vertical-align: top;">总分评级</td>
                    <td style="padding: 8px;">
                        <span style="padding: 2px 10px; border-radius: 12px; font-size: 12px; color: white; background-color:
                        {% if user_info.total_score >= 8.5 %}#27ae60
                        {% elif user_info.total_score >= 7.5 %}#3498db
                        {% elif user_info.total_score >= 6.5 %}#f39c12
                        {% else %}#e74c3c{% endif %};">
                        {% if user_info.total_score >= 8.5 %}优秀
                        {% elif user_info.total_score >= 7.5 %}良好
                        {% elif user_info.total_score >= 6.5 %}一般
                        {% else %}待提升{% endif %}
                        </span>
                    </td>
                </tr>
            </table>
        </div>
    </div>
</div>
<!-- /component -->
"""
        }
    },

    # 添加注意事项组件
    "notice": {
        "disclaimer": {
            "name": "报告免责声明",
            "description": "测评报告的免责声明",
            "html": """
<!-- component:notice id:disclaimer -->
<div style="margin: 20px 0; padding: 15px; background-color: #fff8e1; border-left: 4px solid #ffb300; border-radius: 0 5px 5px 0;">
    <h4 style="color: #bf9800; margin-top: 0;">{{ notice_title|default('报告说明') }}</h4>
    <div style="font-size: 0.9em; line-height: 1.6;">
        <p>{{ disclaimer_content|default('本测评报告结果基于被测者提供的信息，仅作参考之用。报告内容不作为考核的唯一依据，建议与其他测评方法和实际工作表现相结合进行综合评估。') }}</p>
        <p style="margin-top: 10px; font-size: 0.9em;">报告内容严格保密，仅供被授权人员查阅。如有问题请联系人力资源部门。</p>
    </div>
</div>
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
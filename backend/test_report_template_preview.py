import os
import sys
import json
import yaml
import tempfile
import unittest
from pathlib import Path
from datetime import datetime

# 添加项目根目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

# 直接导入预览生成函数
from reports.generators.generate_report import generate_preview_html

class TestReportTemplatePreview(unittest.TestCase):
    """测试报告模板预览功能"""
    
    def setUp(self):
        """设置测试环境"""
        # 准备测试数据
        self.test_html = """<!DOCTYPE html>
<html>
<head>
    <title>测试模板</title>
</head>
<body>
    <h1>{{user_info.name}}的测评报告</h1>
    <p>总分：{{user_info.total_score}}</p>
    <div class="footer">
        <p>此报告由智能评测系统生成 {{ '&copy;' }} {{now.year}} 测评系统</p>
    </div>
</body>
</html>"""
        
        self.test_yaml = """
paper_id: 999
paper_name: "测试试卷"
paper_description: "用于单元测试的测试试卷"
paper_version: "v1.0"
"""
        
        # 创建临时文件
        self.temp_dir = Path("reports/generators/test_temp")
        self.temp_dir.mkdir(exist_ok=True, parents=True)
        
        self.template_path = self.temp_dir / "test_template.html"
        self.config_path = self.temp_dir / "test_config.yaml"
        
        # 写入测试文件
        with open(self.template_path, 'w', encoding='utf-8') as f:
            f.write(self.test_html)
            
        with open(self.config_path, 'w', encoding='utf-8') as f:
            f.write(self.test_yaml)
        
        # 创建测试数据
        self.test_data = {
            "user_info": {
                "name": "测试用户",
                "total_score": 7.8
            },
            "dimensions": {
                "维度1": {"score": 8.5, "subs": {}},
                "维度2": {"score": 7.2, "subs": {}},
                "维度3": {"score": 6.7, "subs": {}}
            },
            "performance_eval": {
                "summary": "表现良好，具备发展潜力",
                "development_focus": "建议加强专业技能培训"
            }
        }
        
    def tearDown(self):
        """清理测试环境"""
        # 删除临时文件
        if self.template_path.exists():
            self.template_path.unlink()
        if self.config_path.exists():
            self.config_path.unlink()
        
        # 尝试删除临时目录
        try:
            self.temp_dir.rmdir()
        except:
            pass
        
    def test_generate_preview(self):
        """测试生成预览HTML"""
        # 调用预览生成函数
        preview_html = generate_preview_html(
            config_path=str(self.config_path),
            template_path=str(self.template_path),
            test_data=self.test_data
        )
        
        # 检查返回结果
        self.assertIsNotNone(preview_html)
        self.assertIsInstance(preview_html, str)
        self.assertGreater(len(preview_html), 100)
        
        # 检查关键内容是否存在
        self.assertIn("测试用户的测评报告", preview_html)
        self.assertIn("总分", preview_html)
        self.assertIn("测评系统", preview_html)
        
        print("预览HTML成功生成，长度:", len(preview_html))
        print("预览HTML前100个字符:", preview_html[:100])
        
        # 可选：保存生成的HTML到文件以便手动检查
        output_dir = Path("reports/generators/output")
        output_dir.mkdir(exist_ok=True, parents=True)
        with open(output_dir / "preview_test.html", "w", encoding="utf-8") as f:
            f.write(preview_html)
        
        print(f"预览HTML已保存到 {output_dir / 'preview_test.html'}")

if __name__ == "__main__":
    unittest.main() 
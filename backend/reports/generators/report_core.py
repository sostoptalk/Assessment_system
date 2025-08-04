import yaml
import pandas as pd
import base64
import os
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path

from config_loader import get_paper_config, get_available_papers
from radar_chart import generate_radar_chart
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML


class UniversalReportGenerator:
    """通用报告生成器 - 支持多种试卷的报告生成"""
    
    def __init__(self, config_dir: str = "configs", template_dir: str = "templates"):
        # 获取当前文件所在目录
        current_dir = Path(__file__).parent
        self.config_dir = current_dir / config_dir
        self.template_dir = current_dir / template_dir
        
        # 确保目录存在
        self.config_dir.mkdir(exist_ok=True)
        self.template_dir.mkdir(exist_ok=True)
        
        # 日志一下搜索路径
        print(f"报告生成器配置目录: {self.config_dir}")
        print(f"报告生成器模板目录: {self.template_dir}")
        
        # 检查备用路径
        self.alt_config_dir = None
        parent_dir = current_dir.parent.parent.parent
        alt_path = parent_dir / "backend" / "reports" / "generators" / "configs"
        if alt_path.exists():
            self.alt_config_dir = alt_path
            print(f"发现备用配置目录: {self.alt_config_dir}")
            
            # 尝试复制文件
            try:
                for file in alt_path.glob("*.yaml"):
                    target_file = self.config_dir / file.name
                    if not target_file.exists():
                        import shutil
                        shutil.copy2(file, target_file)
                        print(f"已复制配置文件: {file.name}")
            except Exception as e:
                print(f"复制配置文件失败: {str(e)}")
        
    def read_excel_data(self, excel_path: str, paper_id: int) -> List[Dict[str, Any]]:
        """
        根据试卷配置读取Excel数据
        
        Args:
            excel_path: Excel文件路径
            paper_id: 试卷ID
            
        Returns:
            标准化后的数据列表
        """
        config = get_paper_config(paper_id)
        field_mapping = config.get('field_mapping', {})
        
        # 读取Excel文件
        df = pd.read_excel(excel_path, engine='openpyxl')
        
        # 应用字段映射
        df.columns = [field_mapping.get(col, col) for col in df.columns]
        
        # 转换为标准数据结构
        report_data_list = []
        for _, row in df.iterrows():
            report_data = {
                "user_info": {
                    "name": row.get('name', ''),
                    "total_score": row.get('total_score', 0)
                },
                "dimensions": {}
            }
            
            # 构建维度数据结构
            for dimension in config['dimensions']:
                dim_name = dimension['name']
                dim_score = row.get(dim_name, 0)
                
                report_data["dimensions"][dim_name] = {
                    "score": dim_score,
                    "subs": {}
                }
                
                # 添加子维度数据
                for sub_dim in dimension['sub_dimensions']:
                    sub_name = sub_dim['name']
                    sub_score = row.get(sub_name, 0)
                    report_data["dimensions"][dim_name]["subs"][sub_name] = sub_score
                    
            report_data_list.append(report_data)
            
        return report_data_list
        
    def prepare_report_data(self, report_data: Dict[str, Any], paper_id: int) -> Dict[str, Any]:
        """
        准备报告数据，包括评价和对比分析
        
        Args:
            report_data: 原始报告数据
            paper_id: 试卷ID
            
        Returns:
            处理后的报告数据
        """
        config = get_paper_config(paper_id)
        
        # 获取总分评价
        total_score = report_data["user_info"]["total_score"]
        performance_level = self._get_performance_level(paper_id, total_score)
        
        report_data["performance_eval"] = performance_level
        report_data["dimension_evaluations"] = {}
        
        # 转换为模板期望的格式
        dimensions_list = []
        # 检查dimensions是字典还是列表
        if isinstance(report_data["dimensions"], dict):
            # 如果是字典格式，转换为列表格式
            for dim_name, dim_data in report_data["dimensions"].items():
                if isinstance(dim_data, dict):
                    score = dim_data.get("score", 0)
                else:
                    score = dim_data  # 如果直接是分数
                eval_data = self._get_dimension_evaluation(paper_id, dim_name, score)
                
                # 创建维度对象
                dimension_obj = {
                    "name": dim_name,
                    "score": score,
                    "avg_score": 7.0,  # 默认平均分
                    "level_key": self._get_evaluation_level(score),
                    "level_description": self._get_level_description(score),
                    "definition": self._get_dimension_definition(config, dim_name),
                    "characteristics": [],
                    "typical_performances": [],
                    "suggestion": "",
                    "subs": {}  # 初始化子维度字典
                }
                # 复制子维度数据
                if isinstance(dim_data, dict) and "subs" in dim_data:
                    dimension_obj["subs"] = dim_data["subs"]
                
                if eval_data:
                    # 处理子维度评价（如果存在）
                    if isinstance(dim_data, dict) and "subs" in dim_data:
                        for sub_name, sub_score in dim_data["subs"].items():
                            if not isinstance(sub_score, (int, float)):
                                continue
                                
                            # 确定子维度评价级别
                            sub_level = self._get_evaluation_level(sub_score)
                            
                            # 获取子维度评价内容
                            if "sub_dimensions" in eval_data and sub_name in eval_data["sub_dimensions"]:
                                sub_eval = eval_data["sub_dimensions"][sub_name]
                                sub_eval["eval_level"] = sub_level
                                
                                dim_data["subs"][sub_name] = {
                                    "score": sub_score,
                                    "evaluation": sub_eval
                                }
                            else:
                                dim_data["subs"][sub_name] = {
                                    "score": sub_score,
                                    "evaluation": None
                                }
                                
                    # 添加大维度评价
                    report_data["dimension_evaluations"][dim_name] = {
                        "dimension_eval": eval_data.get("dimension_eval", ""),
                        "eval_level": self._get_evaluation_level(score)
                    }
                    
                    # 添加特征和表现
                    if "characteristics" in eval_data:
                        dimension_obj["characteristics"] = eval_data["characteristics"]
                    if "typical_performances" in eval_data:
                        dimension_obj["typical_performances"] = eval_data["typical_performances"]
                    if "suggestion" in eval_data:
                        dimension_obj["suggestion"] = eval_data["suggestion"]
                
                dimensions_list.append(dimension_obj)
        else:
            # 如果已经是列表格式
            for dim_data in report_data["dimensions"]:
                dim_name = dim_data["name"]
                score = dim_data["score"]
                eval_data = self._get_dimension_evaluation(paper_id, dim_name, score)
                
                # 创建维度对象
                dimension_obj = {
                    "name": dim_name,
                    "score": score,
                    "avg_score": 7.0,  # 默认平均分
                    "level_key": self._get_evaluation_level(score),
                    "level_description": self._get_level_description(score),
                    "definition": self._get_dimension_definition(config, dim_name),
                    "characteristics": [],
                    "typical_performances": [],
                    "suggestion": "",
                    "subs": {}  # 初始化子维度字典
                }
                # 复制子维度数据
                if isinstance(dim_data, dict) and "subs" in dim_data:
                    dimension_obj["subs"] = dim_data["subs"]
                
                if eval_data:
                    # 处理子维度评价（如果存在）
                    if isinstance(dim_data, dict) and "subs" in dim_data:
                        for sub_name, sub_score in dim_data["subs"].items():
                            if not isinstance(sub_score, (int, float)):
                                continue
                                
                            # 确定子维度评价级别
                            sub_level = self._get_evaluation_level(sub_score)
                            
                            # 获取子维度评价内容
                            if "sub_dimensions" in eval_data and sub_name in eval_data["sub_dimensions"]:
                                sub_eval = eval_data["sub_dimensions"][sub_name]
                                sub_eval["eval_level"] = sub_level
                                
                                dim_data["subs"][sub_name] = {
                                    "score": sub_score,
                                    "evaluation": sub_eval
                                }
                            else:
                                dim_data["subs"][sub_name] = {
                                    "score": sub_score,
                                    "evaluation": None
                                }
                                
                    # 添加大维度评价
                    report_data["dimension_evaluations"][dim_name] = {
                        "dimension_eval": eval_data.get("dimension_eval", ""),
                        "eval_level": self._get_evaluation_level(score)
                    }
                    
                    # 添加特征和表现
                    if "characteristics" in eval_data:
                        dimension_obj["characteristics"] = eval_data["characteristics"]
                    if "typical_performances" in eval_data:
                        dimension_obj["typical_performances"] = eval_data["typical_performances"]
                    if "suggestion" in eval_data:
                        dimension_obj["suggestion"] = eval_data["suggestion"]
                
                dimensions_list.append(dimension_obj)
        
        # 替换为列表格式
        report_data["dimensions"] = dimensions_list
        
        # 添加其他模板需要的字段
        report_data["name"] = report_data["user_info"]["name"]
        report_data["total_score"] = report_data["user_info"]["total_score"]
        report_data["overall_class"] = self._get_overall_class(total_score)
        report_data["overall_performance"] = self._get_overall_performance(total_score)
        report_data["avg_total_score"] = 7.0  # 默认平均分
        report_data["strengths_text"] = "逻辑推理、数据分析"
        report_data["weaknesses_text"] = "战略思维、商业洞察"
        report_data["final_remark"] = "建议继续加强优势领域，同时重点提升待改进的维度。"
        report_data["current_date"] = "2025年5月21日"
        report_data["current_year"] = "2025"
        report_data["logo_url"] = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
        report_data["strengths"] = {
            "总分": {
            "average": report_data["total_score"],  # 或者用一个模拟平均分
            "diff": 0  # 或者用一个模拟差值
            }
        }
        report_data["weaknesses"] = {
            "总分": {
                "average": report_data["total_score"],  # 或者用一个模拟平均分
                "diff": 0  # 或者用一个模拟差值
            }
        }
                
        return report_data
        
    def convert_to_radar_data(self, report_dimensions, paper_id: int) -> list:
        """
        将报告数据转换为雷达图数据
        Args:
            report_dimensions: 报告维度数据（可能是字典或列表格式）
            paper_id: 试卷ID
        Returns:
            雷达图数据
        """
        config = get_paper_config(paper_id)
        radar_data = []
        
        # 处理维度数据格式
        if isinstance(report_dimensions, dict):
            # 如果是字典格式，转换为列表格式
            dimensions_list = []
            for dim_name, dim_data in report_dimensions.items():
                if isinstance(dim_data, dict):
                    score = dim_data.get("score", 0)
                    subs = dim_data.get("subs", {})
                else:
                    score = dim_data  # 如果直接是分数
                    subs = {}
                
                dimensions_list.append({
                    "name": dim_name,
                    "score": score,
                    "subs": subs
                })
            report_dimensions = dimensions_list
        
        for dimension in config['dimensions']:
            dim_name = dimension['name']
            # 在列表中查找对应维度
            report_group = next((d for d in report_dimensions if d['name'] == dim_name), None)
            if not report_group:
                continue
            group_dims = []
            subs = report_group.get('subs', {})
            sub_dim_cfgs = dimension.get('sub_dimensions', [])
            radar_angles = dimension.get('radar_angles', [])
            for idx, sub_dim in enumerate(sub_dim_cfgs):
                sub_name = sub_dim['name']
                angle = radar_angles[idx] if idx < len(radar_angles) else 0
                # 分数优先取subs中的分数，否则为0
                sub_score = subs.get(sub_name, 0)
                if isinstance(sub_score, dict):
                    score_value = sub_score.get("score", 0)
                elif isinstance(sub_score, (int, float)):
                    score_value = sub_score
                else:
                    score_value = 0
                group_dims.append({
                    "name": sub_name,
                    "score": score_value,
                    "angle": angle
                })
            radar_data.append({
                "group": dim_name,
                "color": dimension['color'],
                "dims": group_dims
            })
        return radar_data
        
    def generate_report(self, report_data: Dict[str, Any], paper_id: int, 
                       output_path: str, chart_path: Optional[str] = None) -> str:
        """
        生成PDF报告
        
        Args:
            report_data: 报告数据
            paper_id: 试卷ID
            output_path: 输出路径
            chart_path: 图表路径（可选）
            
        Returns:
            生成的PDF文件路径
        """
        config = get_paper_config(paper_id)
        template_config = config.get('template', {})
        
        # 生成雷达图
        radar_data = self.convert_to_radar_data(report_data['dimensions'], paper_id)
        
        if not chart_path:
            user_name = report_data['user_info']['name']
            chart_filename = f"radar_chart_{user_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            # 确保assets目录存在
            assets_dir = Path(__file__).parent / "assets"
            assets_dir.mkdir(exist_ok=True)
            chart_path = str(assets_dir / chart_filename)
            
        # 生成雷达图文件
        print("雷达图数据：", radar_data)
        generated_chart_path = generate_radar_chart(radar_data, chart_path)
        
        # 检查雷达图生成是否成功
        if generated_chart_path is None:
            raise Exception("雷达图生成失败")
        
        # 设置Jinja2环境
        env = Environment(loader=FileSystemLoader(self.template_dir))
        
        # 添加自定义过滤器
        env.filters.update({
            'get_dim_strengths': self._get_dim_strengths,
            'get_dim_weaknesses': self._get_dim_weaknesses,
            'get_sub_strengths': self._get_sub_strengths,
            'get_sub_weaknesses': self._get_sub_weaknesses,
            'get_top_strength': self._get_top_strength,
            'get_main_weakness': self._get_main_weakness
        })
        
        # 加载模板
        template_name = template_config.get('name', 'report_template.html')
        template = env.get_template(template_name)
        
        # 嵌入图片为Base64
        with open(generated_chart_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
        chart_base64 = f"data:image/png;base64,{encoded_string}"
        
        # 渲染HTML内容
        html_content = template.render(**report_data, chart_img=chart_base64)
        
        # 生成PDF
        try:
            HTML(string=html_content).write_pdf(output_path)
        except TypeError as e:
            if "PDF.__init__() takes 1 positional argument" in str(e):
                # 兼容旧版本的WeasyPrint
                html = HTML(string=html_content)
                html.write_pdf(output_path)
            else:
                raise
        
        return output_path
        
    def batch_generate_reports(self, excel_path: str, paper_id: int, 
                              output_dir: str = "output") -> List[str]:
        """
        批量生成报告
        
        Args:
            excel_path: Excel文件路径
            paper_id: 试卷ID
            output_dir: 输出目录
            
        Returns:
            生成的PDF文件路径列表
        """
        # 确保输出目录存在
        os.makedirs(output_dir, exist_ok=True)
        os.makedirs("assets", exist_ok=True)
        
        # 读取数据
        report_data_list = self.read_excel_data(excel_path, paper_id)
        
        generated_files = []
        
        for report_data in report_data_list:
            try:
                # 准备报告数据
                processed_data = self.prepare_report_data(report_data, paper_id)
                
                # 生成文件名
                user_name = report_data['user_info']['name']
                safe_name = self._sanitize_filename(user_name)
                output_filename = f"{safe_name}_报告_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                output_path = os.path.join(output_dir, output_filename)
                
                # 生成报告
                self.generate_report(processed_data, paper_id, output_path)
                generated_files.append(output_path)
                
                print(f"✅ 成功生成报告: {user_name}")
                
            except Exception as e:
                print(f"❌ 生成 {user_name} 的报告时出错: {str(e)}")
                continue
                
        return generated_files
        
    def _get_performance_level(self, paper_id: int, score: float) -> Optional[Dict[str, Any]]:
        """获取绩效等级评价"""
        config = get_paper_config(paper_id)
        
        for level in config.get('score_levels', []):
            if level['min'] <= score <= level['max']:
                return level
                
        return None
        
    def _get_dimension_evaluation(self, paper_id: int, dimension_name: str, score: float) -> Optional[Dict[str, Any]]:
        """获取维度评价"""
        config = get_paper_config(paper_id)
        level = self._get_evaluation_level(score)
        
        if not level:
            return None
            
        dimension_evaluations = config.get('dimension_evaluations', {})
        if dimension_name not in dimension_evaluations:
            return None
            
        return dimension_evaluations[dimension_name].get(level)
        
    def _get_evaluation_level(self, score: float) -> Optional[str]:
        """根据分数确定评价级别"""
        if score >= 8.5:
            return 'high'
        elif score >= 7.5:
            return 'medium'
        elif score >= 6.5:
            return 'low'
        else:
            return 'bad'
            
    def _get_level_description(self, score: float) -> str:
        """根据分数获取级别描述"""
        if score >= 8.5:
            return "优秀水平"
        elif score >= 7.5:
            return "良好水平"
        elif score >= 6.5:
            return "中等水平"
        else:
            return "基础水平"
            
    def _get_overall_class(self, score: float) -> str:
        """根据总分获取整体表现类别"""
        if score >= 8.5:
            return "high"
        elif score >= 7.5:
            return "medium"
        elif score >= 6.5:
            return "low"
        else:
            return "bad"
            
    def _get_overall_performance(self, score: float) -> str:
        """根据总分获取整体表现描述"""
        if score >= 8.5:
            return "优秀"
        elif score >= 7.5:
            return "良好"
        elif score >= 6.5:
            return "中等"
        else:
            return "基础"
            
    def _get_dimension_definition(self, config: Dict[str, Any], dim_name: str) -> str:
        """从配置中获取维度定义"""
        for dimension in config.get('dimensions', []):
            if dimension.get('name') == dim_name:
                return dimension.get('description', '')
        return ''
            
    def _sanitize_filename(self, name: str) -> str:
        """清理文件名"""
        import re
        import unicodedata
        
        if not name:
            return "unknown"
            
        name = unicodedata.normalize('NFKC', name)
        name = re.sub(r'[\\/*?:"<>|]', '_', name)
        name = name.strip()
        
        if not name:
            name = "unknown"
            
        return name
        
    # 模板过滤器方法
    def _get_dim_strengths(self, strengths):
        return strengths.get("维度", [])
        
    def _get_dim_weaknesses(self, weaknesses):
        return weaknesses.get("维度", [])
        
    def _get_sub_strengths(self, strengths):
        return strengths.get("子维度", [])
        
    def _get_sub_weaknesses(self, weaknesses):
        return weaknesses.get("子维度", [])
        
    def _get_top_strength(self, strengths):
        candidates = strengths.get("维度", []) + strengths.get("子维度", [])
        if not candidates:
            return None
        candidates.sort(key=lambda x: x["diff"], reverse=True)
        return candidates[0]
        
    def _get_main_weakness(self, weaknesses):
        candidates = weaknesses.get("维度", []) + weaknesses.get("子维度", [])
        if not candidates:
            return None
        candidates.sort(key=lambda x: x["diff"])
        return candidates[0]


# 全局报告生成器实例
report_generator = UniversalReportGenerator()


def generate_single_report(paper_id: int, user_data: Dict[str, Any], 
                          output_path: str) -> str:
    """生成单个报告"""
    processed_data = report_generator.prepare_report_data(user_data, paper_id)
    return report_generator.generate_report(processed_data, paper_id, output_path)


def batch_generate_reports(excel_path: str, paper_id: int, 
                          output_dir: str = "output") -> List[str]:
    """批量生成报告"""
    return report_generator.batch_generate_reports(excel_path, paper_id, output_dir)


if __name__ == "__main__":
    # 测试通用报告生成器
    try:
        # 测试获取可用试卷
        papers = get_available_papers()
        print(f"可用试卷: {len(papers)}")
        for paper in papers:
            print(f"  - {paper['paper_name']} (ID: {paper['paper_id']})")
            
        # 测试加载配置
        config = get_paper_config(1)
        print(f"成功加载配置: {config['paper_name']}")
        
    except Exception as e:
        print(f"测试失败: {e}") 
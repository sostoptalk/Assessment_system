#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试报告生成功能
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.append(str(project_root))

# 添加reports目录到Python路径
reports_dir = project_root / "reports" / "generators"
sys.path.append(str(reports_dir))

def test_config_loading():
    """测试配置加载"""
    print("=== 测试配置加载 ===")
    try:
        from reports.generators.config_loader import get_paper_config, get_available_papers
        
        # 测试获取可用试卷
        papers = get_available_papers()
        print(f"可用试卷数量: {len(papers)}")
        for paper in papers:
            print(f"  - {paper['paper_name']} (ID: {paper['paper_id']})")
            
        # 测试加载配置
        config = get_paper_config(16)
        print(f"成功加载试卷配置: {config['paper_name']}")
        print(f"维度数量: {len(config['dimensions'])}")
        
        return True
    except Exception as e:
        print(f"配置加载失败: {e}")
        import traceback
        print(f"详细错误: {traceback.format_exc()}")
        return False

def test_report_generation():
    """测试报告生成"""
    print("\n=== 测试报告生成 ===")
    try:
        from reports.generators.report_core import generate_single_report
        
        # 模拟报告数据
        test_data = {
            "user_info": {
                "id": 1,
                "name": "测试用户",
                "username": "test_user",
                "total_score": 75.5
            },
            "paper_info": {
                "id": 2,
                "name": "商业推理能力测评",
                "description": "测试试卷"
            },
            "dimensions": {
                "逻辑推理": {
                    "score": 80.0,
                    "subs": {
                        "演绎推理": 85,
                        "归纳推理": 78,
                        "类比推理": 77
                    }
                },
                "数据分析": {
                    "score": 72.0,
                    "subs": {
                        "数据解读": 75,
                        "趋势分析": 70,
                        "风险评估": 71
                    }
                },
                "战略思维": {
                    "score": 78.0,
                    "subs": {
                        "全局视角": 80,
                        "创新思维": 76,
                        "决策判断": 78
                    }
                },
                "商业洞察": {
                    "score": 73.0,
                    "subs": {
                        "市场敏感": 75,
                        "竞争分析": 72,
                        "价值创造": 72
                    }
                }
            }
        }
        
        # 生成测试报告
        output_dir = Path(__file__).parent / "reports" / "generators" / "output"
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = str(output_dir / "test_report.pdf")
        
        print(f"开始生成测试报告: {output_path}")
        result = generate_single_report(16, test_data, output_path)
        print(f"报告生成成功: {result}")
        
        return True
    except Exception as e:
        print(f"报告生成失败: {e}")
        import traceback
        print(f"详细错误: {traceback.format_exc()}")
        return False

def main():
    """主函数"""
    print("开始测试报告生成功能...")
    
    # 测试配置加载
    config_ok = test_config_loading()
    
    # 测试报告生成
    report_ok = test_report_generation()
    
    if config_ok and report_ok:
        print("\n✅ 所有测试通过！")
    else:
        print("\n❌ 测试失败！")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main()) 
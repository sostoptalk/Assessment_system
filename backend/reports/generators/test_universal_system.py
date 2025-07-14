#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
通用化报告生成系统测试脚本
测试配置加载、数据处理、报告生成等功能
"""

import os
import sys
import pandas as pd
from pathlib import Path

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config_loader import get_paper_config, get_available_papers, config_loader
from report_core import UniversalReportGenerator, generate_single_report, batch_generate_reports


def test_config_loading():
    """测试配置加载功能"""
    print("=== 测试配置加载功能 ===")
    
    try:
        # 测试获取可用试卷
        papers = get_available_papers()
        print(f"✅ 成功获取可用试卷: {len(papers)} 个")
        for paper in papers:
            print(f"  - {paper['paper_name']} (ID: {paper['paper_id']})")
            
        # 测试加载管理潜质测评配置
        config1 = get_paper_config(1)
        print(f"✅ 成功加载管理潜质测评配置")
        print(f"  - 试卷名称: {config1['paper_name']}")
        print(f"  - 维度数量: {len(config1['dimensions'])}")
        print(f"  - 分数区间: {len(config1['score_levels'])} 个")
        
        # 测试加载商业推理能力配置
        config2 = get_paper_config(2)
        print(f"✅ 成功加载商业推理能力配置")
        print(f"  - 试卷名称: {config2['paper_name']}")
        print(f"  - 维度数量: {len(config2['dimensions'])}")
        print(f"  - 分数区间: {len(config2['score_levels'])} 个")
        
        return True
        
    except Exception as e:
        print(f"❌ 配置加载测试失败: {e}")
        return False


def test_field_mapping():
    """测试字段映射功能"""
    print("\n=== 测试字段映射功能 ===")
    
    try:
        # 测试管理潜质测评的字段映射
        config1 = get_paper_config(1)
        field_mapping1 = config1.get('field_mapping', {})
        print(f"✅ 管理潜质测评字段映射: {len(field_mapping1)} 个字段")
        
        # 测试商业推理能力的字段映射
        config2 = get_paper_config(2)
        field_mapping2 = config2.get('field_mapping', {})
        print(f"✅ 商业推理能力字段映射: {len(field_mapping2)} 个字段")
        
        return True
        
    except Exception as e:
        print(f"❌ 字段映射测试失败: {e}")
        return False


def test_score_levels():
    """测试分数区间功能"""
    print("\n=== 测试分数区间功能 ===")
    
    try:
        # 测试管理潜质测评的分数区间
        config1 = get_paper_config(1)
        score_levels1 = config1.get('score_levels', [])
        print(f"✅ 管理潜质测评分数区间: {len(score_levels1)} 个")
        for level in score_levels1:
            print(f"  - {level['name']}: {level['min']}-{level['max']}")
            
        # 测试商业推理能力的分数区间
        config2 = get_paper_config(2)
        score_levels2 = config2.get('score_levels', [])
        print(f"✅ 商业推理能力分数区间: {len(score_levels2)} 个")
        for level in score_levels2:
            print(f"  - {level['name']}: {level['min']}-{level['max']}")
            
        return True
        
    except Exception as e:
        print(f"❌ 分数区间测试失败: {e}")
        return False


def test_dimension_evaluations():
    """测试维度评价功能"""
    print("\n=== 测试维度评价功能 ===")
    
    try:
        # 测试管理潜质测评的维度评价
        config1 = get_paper_config(1)
        dimension_evaluations1 = config1.get('dimension_evaluations', {})
        print(f"✅ 管理潜质测评维度评价: {len(dimension_evaluations1)} 个维度")
        
        # 测试商业推理能力的维度评价
        config2 = get_paper_config(2)
        dimension_evaluations2 = config2.get('dimension_evaluations', {})
        print(f"✅ 商业推理能力维度评价: {len(dimension_evaluations2)} 个维度")
        
        return True
        
    except Exception as e:
        print(f"❌ 维度评价测试失败: {e}")
        return False


def create_test_data():
    """创建测试数据"""
    print("\n=== 创建测试数据 ===")
    
    try:
        # 创建管理潜质测评测试数据
        management_data = {
            '姓名': ['张三', '李四', '王五'],
            '总分': [8.2, 7.1, 6.8],
            '大维度1：自我成长与发展': [8.5, 7.2, 6.5],
            '小维度1：学习与探索动机': [8.8, 7.5, 6.2],
            '小维度2：寻求和运用反馈': [8.3, 7.0, 6.8],
            '小维度3：情感成熟度': [8.4, 7.1, 6.5],
            '大维度2：管理动力': [8.1, 7.3, 6.9],
            '小维度4：领导意愿': [8.2, 7.4, 6.7],
            '小维度5：追求成就': [8.0, 7.2, 7.1],
            '小维度6：组织意识': [8.1, 7.3, 6.9],
            '大维度3：管理他人': [7.9, 7.0, 6.6],
            '小维度7：人际洞察': [8.0, 7.1, 6.5],
            '小维度8：同理心': [7.8, 6.9, 6.7],
            '小维度9：发挥他人': [7.9, 7.0, 6.6],
            '大维度4：管理事务': [8.3, 7.2, 6.8],
            '小维度10：跨领域思考': [8.4, 7.3, 6.9],
            '小维度11：概念性思维': [8.2, 7.1, 6.7],
            '小维度12：适应变化情境': [8.3, 7.2, 6.8]
        }
        
        # 创建商业推理能力测试数据
        business_data = {
            '姓名': ['赵六', '钱七', '孙八'],
            '总分': [8.7, 7.8, 6.9],
            '大维度1：逻辑推理': [8.8, 7.9, 7.0],
            '小维度1：演绎推理': [8.9, 8.0, 7.1],
            '小维度2：归纳推理': [8.7, 7.8, 6.9],
            '小维度3：类比推理': [8.8, 7.9, 7.0],
            '大维度2：数据分析': [8.6, 7.7, 6.8],
            '小维度4：数据解读': [8.7, 7.8, 6.9],
            '小维度5：趋势分析': [8.5, 7.6, 6.7],
            '小维度6：风险评估': [8.6, 7.7, 6.8],
            '大维度3：战略思维': [8.9, 8.0, 7.1],
            '小维度7：全局视角': [9.0, 8.1, 7.2],
            '小维度8：创新思维': [8.8, 7.9, 7.0],
            '小维度9：决策判断': [8.9, 8.0, 7.1],
            '大维度4：商业洞察': [8.5, 7.6, 6.7],
            '小维度10：市场敏感': [8.6, 7.7, 6.8],
            '小维度11：竞争分析': [8.4, 7.5, 6.6],
            '小维度12：价值创造': [8.5, 7.6, 6.7]
        }
        
        # 保存测试数据
        os.makedirs('test_data', exist_ok=True)
        
        df1 = pd.DataFrame(management_data)
        df1.to_excel('test_data/management_potential_test.xlsx', index=False)
        print("✅ 创建管理潜质测评测试数据: test_data/management_potential_test.xlsx")
        
        df2 = pd.DataFrame(business_data)
        df2.to_excel('test_data/business_reasoning_test.xlsx', index=False)
        print("✅ 创建商业推理能力测试数据: test_data/business_reasoning_test.xlsx")
        
        return True
        
    except Exception as e:
        print(f"❌ 创建测试数据失败: {e}")
        return False


def test_report_generation():
    """测试报告生成功能"""
    print("\n=== 测试报告生成功能 ===")
    
    try:
        # 确保测试数据存在
        if not os.path.exists('test_data/management_potential_test.xlsx'):
            print("❌ 测试数据不存在，请先运行创建测试数据")
            return False
            
        # 测试管理潜质测评报告生成
        print("📊 测试管理潜质测评报告生成...")
        generator = UniversalReportGenerator()
        
        # 读取测试数据
        report_data_list = generator.read_excel_data('test_data/management_potential_test.xlsx', 1)
        print(f"✅ 成功读取 {len(report_data_list)} 条测试数据")
        
        # 处理第一条数据
        if report_data_list:
            test_data = report_data_list[0]
            processed_data = generator.prepare_report_data(test_data, 1)
            print(f"✅ 成功处理报告数据: {processed_data['user_info']['name']}")
            
            # 测试雷达图数据转换
            radar_data = generator.convert_to_radar_data(processed_data['dimensions'], 1)
            print(f"✅ 成功转换雷达图数据: {len(radar_data)} 个维度组")
            
        # 测试商业推理能力报告生成
        if os.path.exists('test_data/business_reasoning_test.xlsx'):
            print("📊 测试商业推理能力报告生成...")
            report_data_list2 = generator.read_excel_data('test_data/business_reasoning_test.xlsx', 2)
            print(f"✅ 成功读取 {len(report_data_list2)} 条测试数据")
            
            if report_data_list2:
                test_data2 = report_data_list2[0]
                processed_data2 = generator.prepare_report_data(test_data2, 2)
                print(f"✅ 成功处理报告数据: {processed_data2['user_info']['name']}")
                
        return True
        
    except Exception as e:
        print(f"❌ 报告生成测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_config_validation():
    """测试配置验证功能"""
    print("\n=== 测试配置验证功能 ===")
    
    try:
        # 测试有效配置
        config1 = get_paper_config(1)
        is_valid1 = config_loader._is_valid_paper_config(config1)
        print(f"✅ 管理潜质测评配置验证: {'通过' if is_valid1 else '失败'}")
        
        config2 = get_paper_config(2)
        is_valid2 = config_loader._is_valid_paper_config(config2)
        print(f"✅ 商业推理能力配置验证: {'通过' if is_valid2 else '失败'}")
        
        return is_valid1 and is_valid2
        
    except Exception as e:
        print(f"❌ 配置验证测试失败: {e}")
        return False


def main():
    """主测试函数"""
    print("🚀 开始通用化报告生成系统测试")
    print("=" * 50)
    
    # 确保配置目录存在
    os.makedirs('configs', exist_ok=True)
    os.makedirs('templates', exist_ok=True)
    os.makedirs('output', exist_ok=True)
    
    # 运行各项测试
    tests = [
        ("配置加载", test_config_loading),
        ("字段映射", test_field_mapping),
        ("分数区间", test_score_levels),
        ("维度评价", test_dimension_evaluations),
        ("配置验证", test_config_validation),
        ("创建测试数据", create_test_data),
        ("报告生成", test_report_generation),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} 测试通过")
            else:
                print(f"❌ {test_name} 测试失败")
        except Exception as e:
            print(f"❌ {test_name} 测试异常: {e}")
            
    print("\n" + "=" * 50)
    print(f"📊 测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！通用化报告生成系统运行正常")
    else:
        print("⚠️  部分测试失败，请检查配置和代码")
        
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 
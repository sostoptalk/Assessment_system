from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
import base64
import radar_chart
import os
import re
import unicodedata
from datetime import datetime
import pandas as pd
from tqdm import tqdm

def read_excel_to_report_data_list(file_path):
    """
    从Excel文件读取多个人才数据，并转换为report_data列表
    """
    # 读取Excel文件
    df = pd.read_excel(file_path, engine='openpyxl')

    # 列名映射字典 (从Excel列名到代码中使用的名称)
    column_mapping = {
        '姓名': 'name',
        '总分': 'total_score',
        '大维度1：自我成长与发展': '自我成长与发展',
        '小维度1：学习与探索动机': '学习与探索动机',
        '小维度2：寻求和运用反馈': '寻求和运用反馈',
        '小维度3：情感成熟度': '情感成熟度',
        '大维度2：管理动力': '管理动力',
        '小维度4：领导意愿': '领导意愿',
        '小维度5：追求成就': '追求成就',
        '小维度6：组织意识': '组织意识',
        '大维度3：管理他人': '管理他人',
        '小维度7：人际洞察': '人际洞察',
        '小维度8：同理心': '同理心',
        '小维度9：发挥他人': '发挥他人',
        '大维度4：管理事务': '管理事务',
        '小维度10：跨领域思考': '跨领域思考',
        '小维度11：概念性思维': '概念性思维',
        '小维度12：适应变化情境': '适应变化情景'
    }

    # 简化列名（移除前缀）
    df.columns = [column_mapping.get(col, col) for col in df.columns]

    report_data_list = []
    for _, row in df.iterrows():
        # 创建数据结构
        report_data = {
            "user_info": {
                "name": row['name'],
                "total_score": row['total_score']
            },
            "dimensions": {
                "自我成长与发展": {
                    "score": row['自我成长与发展'],
                    "subs": {
                        "学习与探索动机": row['学习与探索动机'],
                        "寻求和运用反馈": row['寻求和运用反馈'],
                        "情感成熟度": row['情感成熟度']
                    }
                },
                "管理动力": {
                    "score": row['管理动力'],
                    "subs": {
                        "领导意愿": row['领导意愿'],
                        "追求成就": row['追求成就'],
                        "组织意识": row['组织意识']
                    }
                },
                "管理他人": {
                    "score": row['管理他人'],
                    "subs": {
                        "人际洞察": row['人际洞察'],
                        "同理心": row['同理心'],
                        "发挥他人": row['发挥他人']
                    }
                },
                "管理事务": {
                    "score": row['管理事务'],
                    "subs": {
                        "跨领域思考": row['跨领域思考'],
                        "概念性思维": row['概念性思维'],
                        "适应变化情景": row['适应变化情景']
                    }
                }
            }
        }
        report_data_list.append(report_data)

    return report_data_list


def read_excel_with_averages(file_path):
    """
    读取Excel文件，并提取平均分数据
    返回两个结果：人才数据列表和平均分字典
    """
    # 读取Excel文件
    df = pd.read_excel(file_path, engine='openpyxl')

    # 列名映射
    column_mapping = {
        '姓名': 'name',
        '总分': 'total_score',
        '大维度1：自我成长与发展': '自我成长与发展',
        '小维度1：学习与探索动机': '学习与探索动机',
        '小维度2：寻求和运用反馈': '寻求和运用反馈',
        '小维度3：情感成熟度': '情感成熟度',
        '大维度2：管理动力': '管理动力',
        '小维度4：领导意愿': '领导意愿',
        '小维度5：追求成就': '追求成就',
        '小维度6：组织意识': '组织意识',
        '大维度3：管理他人': '管理他人',
        '小维度7：人际洞察': '人际洞察',
        '小维度8：同理心': '同理心',
        '小维度9：发挥他人': '发挥他人',
        '大维度4：管理事务': '管理事务',
        '小维度10：跨领域思考': '跨领域思考',
        '小维度11：概念性思维': '概念性思维',
        '小维度12：适应变化情境': '适应变化情景'
    }

    # 简化列名
    df.columns = [column_mapping.get(col, col) for col in df.columns]

    # 提取平均分行（最后一行）
    average_row = df.iloc[-1].copy()

    # 创建平均分字典
    average_scores = {
        "总分": average_row['total_score'],
        "维度": {},
        "子维度": {}
    }

    # 添加维度平均分
    for dim in ['自我成长与发展', '管理动力', '管理他人', '管理事务']:
        average_scores["维度"][dim] = average_row[dim]

    # 添加子维度平均分
    for sub_dim in ['学习与探索动机', '寻求和运用反馈', '情感成熟度',
                    '领导意愿', '追求成就', '组织意识',
                    '人际洞察', '同理心', '发挥他人',
                    '跨领域思考', '概念性思维', '适应变化情景']:
        average_scores["子维度"][sub_dim] = average_row[sub_dim]

    # 只保留人才数据行（排除最后一行平均分行）
    talent_df = df.iloc[:-1]

    # 转换为人才数据列表
    report_data_list = []
    for _, row in talent_df.iterrows():
        report_data = {
            "user_info": {
                "name": row['name'],
                "total_score": row['total_score']
            },
            "dimensions": {
                "自我成长与发展": {
                    "score": row['自我成长与发展'],
                    "subs": {
                        "学习与探索动机": row['学习与探索动机'],
                        "寻求和运用反馈": row['寻求和运用反馈'],
                        "情感成熟度": row['情感成熟度']
                    }
                },
                "管理动力": {
                    "score": row['管理动力'],
                    "subs": {
                        "领导意愿": row['领导意愿'],
                        "追求成就": row['追求成就'],
                        "组织意识": row['组织意识']
                    }
                },
                "管理他人": {
                    "score": row['管理他人'],
                    "subs": {
                        "人际洞察": row['人际洞察'],
                        "同理心": row['同理心'],
                        "发挥他人": row['发挥他人']
                    }
                },
                "管理事务": {
                    "score": row['管理事务'],
                    "subs": {
                        "跨领域思考": row['跨领域思考'],
                        "概念性思维": row['概念性思维'],
                        "适应变化情景": row['适应变化情景']
                    }
                }
            }
        }
        report_data_list.append(report_data)

    return report_data_list, average_scores


def compare_with_average(report_data, average_scores):
    """
    将个人得分与平均分比较，确定优势项和劣势项
    处理prepare_report_data后的数据结构
    """
    # 初始化优势项和劣势项
    if "strengths" not in report_data:
        report_data["strengths"] = {"维度": [], "子维度": []}
    if "weaknesses" not in report_data:
        report_data["weaknesses"] = {"维度": [], "子维度": []}

    # 总分比较
    user_total = report_data["user_info"]["total_score"]
    avg_total = average_scores.get("总分", 0)

    # 维度得分比较
    for dim_name, dim_data in report_data["dimensions"].items():
        # 获取维度得分（浮点数）
        dim_score = dim_data["score"]

        # 检查维度是否在平均分数据中
        if dim_name in average_scores["维度"]:
            avg_dim_score = average_scores["维度"][dim_name]

            # 维度级别比较
            if dim_score > avg_dim_score:
                report_data["strengths"]["维度"].append({
                    "name": dim_name,
                    "score": dim_score,
                    "average": avg_dim_score,
                    "diff": dim_score - avg_dim_score
                })
            elif dim_score < avg_dim_score:
                report_data["weaknesses"]["维度"].append({
                    "name": dim_name,
                    "score": dim_score,
                    "average": avg_dim_score,
                    "diff": dim_score - avg_dim_score
                })

            # 子维度级别比较
            for sub_name, sub_data in dim_data["subs"].items():
                # 获取子维度得分（兼容原始数值和处理后的字典两种结构）
                if isinstance(sub_data, dict) and "score" in sub_data:
                    # 处理后的字典结构
                    sub_score = sub_data["score"]
                elif isinstance(sub_data, (int, float)):
                    # 原始的数值结构
                    sub_score = sub_data
                else:
                    # 未知结构，跳过
                    continue

                # 检查子维度是否在平均分数据中
                if sub_name in average_scores["子维度"]:
                    avg_sub_score = average_scores["子维度"][sub_name]

                    # 子维度比较
                    if sub_score > avg_sub_score:
                        report_data["strengths"]["子维度"].append({
                            "name": sub_name,
                            "score": sub_score,
                            "average": avg_sub_score,
                            "diff": sub_score - avg_sub_score
                        })
                    elif sub_score < avg_sub_score:
                        report_data["weaknesses"]["子维度"].append({
                            "name": sub_name,
                            "score": sub_score,
                            "average": avg_sub_score,
                            "diff": sub_score - avg_sub_score
                        })

    # 总分比较（放在最后）
    if user_total > avg_total:
        report_data["strengths"]["总分"] = {
            "score": user_total,
            "average": avg_total,
            "diff": user_total - avg_total
        }
    else:
        report_data["weaknesses"]["总分"] = {
            "score": user_total,
            "average": avg_total,
            "diff": user_total - avg_total
        }

    # 对优势和劣势进行排序
    report_data["strengths"]["维度"].sort(key=lambda x: x["diff"], reverse=True)
    report_data["strengths"]["子维度"].sort(key=lambda x: x["diff"], reverse=True)
    report_data["weaknesses"]["维度"].sort(key=lambda x: x["diff"])
    report_data["weaknesses"]["子维度"].sort(key=lambda x: x["diff"])

    return report_data


# def compare_with_average(report_data, average_scores):
#     """
#     将个人得分与平均分比较，确定优势项和劣势项
#     """
#     # 确保优势项和劣势项列表存在
#     if "strengths" not in report_data:
#         report_data["strengths"] = {"维度": [], "子维度": []}
#     if "weaknesses" not in report_data:
#         report_data["weaknesses"] = {"维度": [], "子维度": []}
#
#     # 总分比较
#     if report_data["user_info"]["total_score"] > average_scores["总分"]:
#         report_data["strengths"]["总分"] = report_data["user_info"]["total_score"]
#     else:
#         report_data["weaknesses"]["总分"] = report_data["user_info"]["total_score"]
#
#     # 维度得分比较
#     for dim_name, dim_data in report_data["dimensions"].items():
#         # 确保维度在平均分数据中存在
#         if dim_name in average_scores["维度"]:
#             # 维度级别比较
#             if dim_data["score"] > average_scores["维度"][dim_name]:
#                 report_data["strengths"]["维度"].append({
#                     "name": dim_name,
#                     "score": dim_data["score"],
#                     "average": average_scores["维度"][dim_name]
#                 })
#             elif dim_data["score"] < average_scores["维度"][dim_name]:
#                 report_data["weaknesses"]["维度"].append({
#                     "name": dim_name,
#                     "score": dim_data["score"],
#                     "average": average_scores["维度"][dim_name]
#                 })
#
#             # 子维度级别比较
#             for sub_name, sub_score in dim_data["subs"].items():
#                 # 确保子维度在平均分数据中存在
#                 if sub_name in average_scores["子维度"]:
#                     if sub_score > average_scores["子维度"][sub_name]:
#                         report_data["strengths"]["子维度"].append({
#                             "name": sub_name,
#                             "score": sub_score,
#                             "average": average_scores["子维度"][sub_name]
#                         })
#                     elif sub_score < average_scores["子维度"][sub_name]:
#                         report_data["weaknesses"]["子维度"].append({
#                             "name": sub_name,
#                             "score": sub_score,
#                             "average": average_scores["子维度"][sub_name]
#                         })
#
#     return report_data


# report_data = {
#     "user_info": {
#         "name": "苏发嘉",
#         "total_score": 7.04
#     },
#     "dimensions": {
#         "自我成长与发展": {
#             "score": 6.13,
#             "subs": {
#                 "学习与探索动机": 5,
#                 "寻求和运用反馈": 5.2,
#                 "情感成熟度": 8.2
#             }
#         },
#         "管理动力": {
#             "score": 8.28,
#             "subs": {
#                 "领导意愿": 8.2,
#                 "追求成就": 7.4,
#                 "组织意识": 9.25
#             }
#         },
#         "管理他人": {
#             "score": 7.93,
#             "subs": {
#                 "人际洞察": 9,
#                 "同理心": 8,
#                 "发挥他人": 6.8
#             }
#         },
#         "管理事务": {
#             "score": 7.20,
#             "subs": {
#                 "跨领域思考": 8.2,
#                 "概念性思维": 7.2,
#                 "适应变化情景": 6.2
#             }
#         }
#     }
# }

PERFORMANCE_LEVELS = {
    "high_performance": {
        "score_range": [8.5, 10],
        "summary": "说明其具有卓越的领导潜质，在领导力通道上具备快速晋升的强劲潜力。这类人才不仅能在更高层级的领导角色上持续创造卓越绩效，且有潜力在战略层面引领组织变革与发展。",
        "development_focus": "需着重培养其战略领导力与跨体系协同能力，同时防范长期高压环境下的倦怠风险"
    },
    "high_medium_performance": {
        "score_range": [7.5, 8.4],
        "summary": "说明其具备可培养的领导潜质基础，经过系统化训练可能在2-3年内胜任更高层级的领导角色。在匹配其优势领域的管理岗位上具备产出高绩效的潜力，但需强化关键能力的突破性成长。",
        "development_focus": "应制定针对性发展计划，重点补足跨维度能力短板"
    },
    "medium_performance": {
        "score_range": [6.5, 7.4],
        "summary": "说明其具备可培养的领导潜质基础，经过系统化训练可能在2-3年内胜任更高层级的领导角色。在匹配其优势领域的管理岗位上具备产出高绩效的潜力，但需强化关键能力的突破性成长。",
        "development_focus": "应制定针对性发展计划，重点补足跨维度能力短板"
    },
    "low_performance": {
        "score_range": [1, 6.4],
        "summary": "说明其当前领导潜质基础尚未成形，在现有岗位需至少1-2年的能力沉淀。现阶段较难承接更高层级的领导职责，建议优先在本职领域建立专业影响力，同步提升核心管理维度的基本素养。",
        "development_focus": "需优先激活自我成长意识，夯实情绪管理与基础事务处理能力"
    }
}

DIMENSION_EVALUATIONS = {
    "自我成长与发展": {
        "high": {
            "大维度评价": "展现出卓越的成长内驱力，系统化构建个人发展路径。能够精准把握学习机会，成熟运用反馈机制实现持续迭代，在压力情境中保持情绪韧性，形成自我成长的良性循环。",
            "子维度评价": {
                "学习与探索动机": {
                  "潜质特点": "具备强烈的好奇心和认知拓展热情，主动挑战能力舒适区。将陌生领域视为成长契机，持续构建跨领域知识体系",
                  "工作中的倾向": "在日常工作中创造学习机会，主动承担未知领域的任务；建立行业信息网络，将新知识快速转化为实践能力"
                },
                "寻求和运用反馈": {
                  "潜质特点": "建立常态化反馈获取机制，将批评意见转化为成长燃料。能识别不同来源反馈的价值差异，选择性融合多维信息",
                  "工作中的倾向": "周期性主动寻求360度反馈；建立反馈转化日志，在关键决策前专门征求反对意见；推动团队形成反馈文化"
                },
                "情感成熟度": {
                  "潜质特点": "在高强度压力下保持决策理性，将挫折转化为成长养分。具备情绪预警机制，在情绪波动前主动调节",
                  "工作中的倾向": "面对项目失败时引领团队复盘学习；在高风险决策中保持理性客观；建立个人情绪恢复仪式"
                }
            }
        }, # 高分区间评价
        "medium": {
            "大维度评价": "具备基础成长意识但缺乏系统规划。在熟悉领域学习主动性强，但面对未知领域存在畏惧；能接受直接反馈但转化效率不足；情绪管理呈阶段性波动。",
            "子维度评价": {
                "学习与探索动机": {
                  "潜质特点": "在擅长领域保持学习热情，但对能力短板领域回避探索。学习驱动力受外部目标牵引强于内在好奇",
                  "工作中的倾向": "愿意参与公司组织的培训，但较少自发拓展；面对新任务时需要明确指导而非自主探索"
                },
                "寻求和运用反馈": {
                  "潜质特点": "能接受上级直接反馈但回避同级评价。对建设性意见需要消化时间，偶尔出现选择性接受",
                  "工作中的倾向": "考核期会主动寻求反馈但缺乏连续性；能够参照明确建议改进工作，但难以转化模糊意见"
                },
                "情感成熟度": {
                  "潜质特点": "普通压力下表现稳定，但重大挫折时情绪恢复期较长。能意识到情绪变化但调节手段单一",
                  "工作中的倾向": "常规工作压力下保持正常状态；项目受挫时需2-3天恢复期；面对连续挫折可能出现判断偏差"
                }
            }
        }, # 中分区间评价
        "low": {
            "大维度评价": "成长主动性薄弱，反馈回避倾向明显。学习局限于岗位必需技能，对反馈持防御心态，情绪波动显著影响工作表现。",
            "子维度评价": {
                "学习与探索动机": {
                  "潜质特点": "存在明显学习舒适区，对新领域产生本能排斥。将能力短板视为不可变因素",
                  "工作中的倾向": "拒绝跨职能任务机会；沿用固定工作方法；知识更新滞后岗位要求"
                },
                "寻求和运用反馈": {
                  "潜质特点": "将反馈视为负面评价，产生自我辩护机制。建设性意见常触发抵触情绪",
                  "工作中的倾向": "对反馈建议解释为认知差异；改进措施流于表面；重要决策回避征求他人意见"
                },
                "情感成熟度": {
                  "潜质特点": "情绪调节能力薄弱，挫折后易陷入消极循环。将工作困难归因为外部因素",
                  "工作中的倾向": "压力下出现决策瘫痪；项目受挫后影响后续任务表现；情绪波动传染团队氛围"
                }
            }
        }, # 低分区间评价
        "bad": {
            "大维度评价": "成长主动性薄弱，反馈回避倾向明显。学习局限于岗位必需技能，对反馈持防御心态，情绪波动显著影响工作表现。",
            "子维度评价": {
                "学习与探索动机": {
                  "潜质特点": "存在明显学习舒适区，对新领域产生本能排斥。将能力短板视为不可变因素",
                  "工作中的倾向": "拒绝跨职能任务机会；沿用固定工作方法；知识更新滞后岗位要求"
                },
                "寻求和运用反馈": {
                  "潜质特点": "将反馈视为负面评价，产生自我辩护机制。建设性意见常触发抵触情绪",
                  "工作中的倾向": "对反馈建议解释为认知差异；改进措施流于表面；重要决策回避征求他人意见"
                },
                "情感成熟度": {
                  "潜质特点": "情绪调节能力薄弱，挫折后易陷入消极循环。将工作困难归因为外部因素",
                  "工作中的倾向": "压力下出现决策瘫痪；项目受挫后影响后续任务表现；情绪波动传染团队氛围"
                }
            }
        } # 低分区间评价
    },
    "管理他人": {
        "high": {
            "大维度评价": "具备卓越的人际影响艺术，精准把握团队情感脉搏。能深度解读非语言信号，自然融入他人视角决策，系统化培养人才梯队，构建高信任度团队生态。",
            "子维度评价": {
                "人际洞察": {
                  "潜质特点": "敏锐捕捉微表情、语气变化等非语言信号，精准判断未言明的核心诉求。能预判人际关系发展轨迹，识别潜在合作与冲突点",
                  "工作中的倾向": "会议中实时观察多方反应调整沟通策略；预判利益相关方潜在顾虑；提前化解团队摩擦"
                },
                "同理心": {
                  "潜质特点": "达成情感共振与认知融合的深度理解，能还原他人决策逻辑。在保持自我立场同时内化多元视角",
                  "工作中的倾向": "冲突调解时展现多立场整合能力；跨部门协作中主动设计共赢方案；制度设计融入人性化考量"
                },
                "发挥他人": {
                  "潜质特点": "建立人才赋能系统，精准匹配发展机会与个人特质。将他人成功视为组织资本增值",
                  "工作中的倾向": "系统性实施岗位轮换计划；创建个性化发展路径图；主动让渡关键机会培养继任者"
                }
            }
        },
        "medium": {
            "大维度评价": "具备基础人际理解能力但深度不足。能识别显性情绪信号但忽略潜在动机，在熟悉情境中展现同理心，人才开发聚焦任务需求而非长远发展。",
            "子维度评价": {
                "人际洞察": {
                  "潜质特点": "能捕捉明显情绪变化但解读存在时滞。对常规行为模式有认知，非常规信号易误判",
                  "工作中的倾向": "日常沟通能感知对方情绪基调；复杂会议需要事后复盘才能理解潜台词；偶有过度解读中性表达"
                },
                "同理心": {
                  "潜质特点": "在相似背景同事间展现理解，差异较大时出现认知盲区。情感共鸣强于立场融合",
                  "工作中的倾向": "能理解部门内部诉求但跨职能协作困难；可执行标准化安抚流程；难以协调深层价值观冲突"
                },
                "发挥他人": {
                  "潜质特点": "基于任务需求分配机会，培养动作呈现碎片化。关注即战力多于潜能开发",
                  "工作中的倾向": "按能力匹配当前任务；提供基础指导但缺发展体系；人才推荐依赖显性业绩数据"
                }
            }
        },
        "low": {
            "大维度评价": "人际理解存在显著障碍，常误判他人意图。决策过度自我中心化，人员管理侧重事务分配忽视成长赋能。",
            "子维度评价": {
                "人际洞察": {
                  "潜质特点": "对非语言信号感知迟钝，常将社交礼仪误解为真实态度。行为归因存在刻板印象",
                  "工作中的倾向": "忽略会议中的反对信号；将沉默误认为认同；对离职征兆反应滞后"
                },
                "同理心": {
                  "潜质特点": "情感理解存在认知屏障，常将不同立场视为对抗。归因时过度强调个人责任",
                  "工作中的倾向": "坚持己见导致决策僵局；跨文化沟通频发摩擦；制度执行缺乏弹性空间"
                },
                "发挥他人": {
                  "潜质特点": "视团队成员为执行工具，发展投入视为资源消耗。机会分配倾向控制而非赋能",
                  "工作中的倾向": "任务分配忽略个体差异；重要机会集中亲信；反馈聚焦差错而非成长"
                }
            }
        },
        "bad": {
            "大维度评价": "人际理解存在显著障碍，常误判他人意图。决策过度自我中心化，人员管理侧重事务分配忽视成长赋能。",
            "子维度评价": {
                "人际洞察": {
                    "潜质特点": "对非语言信号感知迟钝，常将社交礼仪误解为真实态度。行为归因存在刻板印象",
                    "工作中的倾向": "忽略会议中的反对信号；将沉默误认为认同；对离职征兆反应滞后"
                },
                "同理心": {
                    "潜质特点": "情感理解存在认知屏障，常将不同立场视为对抗。归因时过度强调个人责任",
                    "工作中的倾向": "坚持己见导致决策僵局；跨文化沟通频发摩擦；制度执行缺乏弹性空间"
                },
                "发挥他人": {
                    "潜质特点": "视团队成员为执行工具，发展投入视为资源消耗。机会分配倾向控制而非赋能",
                    "工作中的倾向": "任务分配忽略个体差异；重要机会集中亲信；反馈聚焦差错而非成长"
                }
            }
        }
    },
    "管理事务": {
        "high": {
            "大维度评价": "具备战略级事务处理架构能力，在高度复杂情境中展现卓越的问题破解艺术。能构建多维联结框架洞察系统关联，将抽象概念转化为可执行方案，主动引领组织变革进程。",
            "子维度评价": {
                "跨领域思考": {
                  "潜质特点": "形成全域知识熔断机制，在迥异领域间建立高价值关联。将跨界信息转化为创新杠杆，识别隐性系统连接点",
                  "工作中的倾向": "主持跨部门项目时创造技术-市场-供应链三元模型；用生物系统原理优化生产流程；构建行业交叉创新智库"
                },
                "概念性思维": {
                  "潜质特点": "发展多维抽象建模能力，实现九层问题解构与重构。精准剥离非本质要素，核心变量控制精度达95%以上",
                  "工作中的倾向": "将百万级用户数据抽象为三阶增长引擎；用物理场论设计组织协作网络；复杂决策时实施五级过滤机制"
                },
                "适应变化情境": {
                  "潜质特点": "将变革转化为组织进化动能，构建预见性适应体系。在VUCA环境中创造稳定输出范式，实现反脆弱成长",
                  "工作中的倾向": "主动实施三个月组织架构迭代周期；创建变革收益可视化仪表盘；设计压力测试沙盘演练机制"
                }
            }
        },
        "medium": {
            "大维度评价": "具备常规事务处理能力但系统性不足。能应对标准化复杂场景，全局视角存在局部盲区；概念提炼停留在现象层级，适应性表现为被动调整而非主动进化。",
            "子维度评价": {
                "跨领域思考": {
                  "潜质特点": "在关联领域能建立基础连接，但价值转化效率有限。跨界思维依赖外部触发，创新关联存在随机性",
                  "工作中的倾向": "可完成跨部门协作基础流程；需要框架模板引导联想；创新方案常停留在概念层难以落地"
                },
                "概念性思维": {
                  "潜质特点": "对中度复杂问题具备解构能力，核心变量识别准确率70%左右。归因分析存在表层化倾向，方法论移植能力弱",
                  "工作中的倾向": "能梳理基础业务流程框架；需要多次迭代才能确定关键要素；面对全新问题类型需外部支持"
                },
                "适应变化情境": {
                  "潜质特点": "适应过程伴随效能波动，变革初期存在本能抗拒。调整周期与变化强度正相关，需明确收益引导",
                  "工作中的倾向": "组织调整后需1-2月恢复期；政策变更时出现短期效能下降；能在指导下建立新工作模式"
                }
            }
        },
        "low": {
            "大维度评价": "事务处理能力局限在单一线性维度。面临复杂信息时出现认知超载，决策依赖经验复制而非本质洞察，变革适应性存在系统性障碍。",
            "子维度评价": {
                "跨领域思考": {
                  "潜质特点": "认知边界锁定在专业孤岛，跨域信息视为干扰噪声。关联尝试引发认知混乱，创新路径依赖机械复制",
                  "工作中的倾向": "拒绝参与跨职能项目；用本部门标准解决全域问题；创新会议中坚持原有方案"
                },
                "概念性思维": {
                  "潜质特点": "陷入细节沼泽无法抽离，现象与本质混淆严重。复杂信息触发决策瘫痪，关键因子识别率低于40%",
                  "工作中的倾向": "百页报告无法提炼三要点；新问题直接套用旧方案；分析会议纠缠非核心细节"
                },
                "适应变化情境": {
                  "潜质特点": "变革触发防御性行为模式，将调整视为能力否定。适应周期远超合理范围，隐性抵制行为持续存在",
                  "工作中的倾向": "组织调整后三个月仍抵触新流程；政策变更时传播消极预期；关键系统升级时坚持传统操作"
                }
            }
        },
        "bad": {
            "大维度评价": "事务处理能力局限在单一线性维度。面临复杂信息时出现认知超载，决策依赖经验复制而非本质洞察，变革适应性存在系统性障碍。",
            "子维度评价": {
                "跨领域思考": {
                    "潜质特点": "认知边界锁定在专业孤岛，跨域信息视为干扰噪声。关联尝试引发认知混乱，创新路径依赖机械复制",
                    "工作中的倾向": "拒绝参与跨职能项目；用本部门标准解决全域问题；创新会议中坚持原有方案"
                },
                "概念性思维": {
                    "潜质特点": "陷入细节沼泽无法抽离，现象与本质混淆严重。复杂信息触发决策瘫痪，关键因子识别率低于40%",
                    "工作中的倾向": "百页报告无法提炼三要点；新问题直接套用旧方案；分析会议纠缠非核心细节"
                },
                "适应变化情境": {
                    "潜质特点": "变革触发防御性行为模式，将调整视为能力否定。适应周期远超合理范围，隐性抵制行为持续存在",
                    "工作中的倾向": "组织调整后三个月仍抵触新流程；政策变更时传播消极预期；关键系统升级时坚持传统操作"
                }
            }
        }
    },
    "管理动力": {
        "high": {
            "大维度评价": "展现出卓越的领导引擎效能，具有强烈的内驱力与使命必达的坚韧意志。主动承担挑战性目标，将个人抱负与组织发展深度绑定，在压力情境下仍能坚持价值主张，持续推动组织前进。",
            "子维度评价": {
                "领导意愿": {
                  "潜质特点": "具有天然的领导磁场与影响力，面对分歧时善用建设性冲突达成共识。将不同观点视为战略优化的契机而非威胁",
                  "工作中的倾向": "在战略会议上坚定表达核心主张；主动接手跨部门攻坚项目；建立观点碰撞的机制化决策流程"
                },
                "追求成就": {
                  "潜质特点": "设置突破性成长目标作为自我驱动核心，将挑战极限视为价值实现路径。成就标准随能力提升动态上移",
                  "工作中的倾向": "制定超越行业平均的业绩目标；创建季度突破性成果追踪机制；将个人发展计划与组织战略绑定"
                },
                "组织意识": {
                  "潜质特点": "实现组织价值观的深度内化，在关键决策时本能选择集体最优解。视组织成功为个人成就的放大器",
                  "工作中的倾向": "主动让渡个人资源支持组织战略；危机时刻率先做出奉献示范；建立组织利益优先的决策评估矩阵"
                }
            }
        },
        "medium": {
            "大维度评价": "具备基础管理意愿但驱动力存在波动。在低阻力环境下能展现领导姿态，面对挑战时易显现目标游离；认同组织价值但关键抉择时常显露个人本位倾向。",
            "子维度评价": {
                "领导意愿": {
                  "潜质特点": "常规情境下愿意指导他人，遇强阻力时转向妥协。影响他人的深度和广度受环境约束",
                  "工作中的倾向": "能主持部门例会布置任务；被质疑时解释而非说服；回避涉及利益调整的关键决策"
                },
                "追求成就": {
                  "潜质特点": "设定安全边际内的成长目标，成就满足点易受外部参照影响。将努力过程部分替代结果价值",
                  "工作中的倾向": "达成KPI后减弱突破动力；重要项目需额外激励措施；规避成功率低于70%的挑战"
                },
                "组织意识": {
                  "潜质特点": "认知层面认同组织理念，但行动层面存在条件性承诺。利益冲突时启动成本收益分析",
                  "工作中的倾向": "常规事务展现奉献精神；重大个人损失时犹豫反复；需要制度保障维持组织忠诚度"
                }
            }
        },
        "low": {
            "大维度评价": "管理驱动力系统尚未激活。领导角色被视为负担而非机遇，成就定位模糊且满足阈值低，组织意识停留在契约义务层面。",
            "子维度评价": {
                "领导意愿": {
                  "潜质特点": "对决策责任产生本能回避，视领导行为为额外负担。观点输出局限于安全话题",
                  "工作中的倾向": "会议中避免提出明确意见；将职责推诿给上级；关键场合保持沉默"
                },
                "追求成就": {
                  "潜质特点": "安于事务性工作舒适区，视挑战为不必要风险。完成基本要求即为满足",
                  "工作中的倾向": "拒绝承担挑战性指标；将额外努力视为无效投入；成果总结聚焦完成而非优化"
                },
                "组织意识": {
                  "潜质特点": "组织概念等价于劳动合同，个人便利优先于集体需要",
                  "工作中的倾向": "严格按岗位说明书执行；利用制度漏洞谋取私利；危机时优先考虑离职选项"
                }
            }
        },
        "bad": {
            "大维度评价": "管理驱动力系统尚未激活。领导角色被视为负担而非机遇，成就定位模糊且满足阈值低，组织意识停留在契约义务层面。",
            "子维度评价": {
                "领导意愿": {
                    "潜质特点": "对决策责任产生本能回避，视领导行为为额外负担。观点输出局限于安全话题",
                    "工作中的倾向": "会议中避免提出明确意见；将职责推诿给上级；关键场合保持沉默"
                },
                "追求成就": {
                    "潜质特点": "安于事务性工作舒适区，视挑战为不必要风险。完成基本要求即为满足",
                    "工作中的倾向": "拒绝承担挑战性指标；将额外努力视为无效投入；成果总结聚焦完成而非优化"
                },
                "组织意识": {
                    "潜质特点": "组织概念等价于劳动合同，个人便利优先于集体需要",
                    "工作中的倾向": "严格按岗位说明书执行；利用制度漏洞谋取私利；危机时优先考虑离职选项"
                }
            }
        },
    }
}


def get_performance_evaluation(total_score):
    """根据总分确定绩效级别和评语"""
    for level, criteria in PERFORMANCE_LEVELS.items():
        min_score, max_score = criteria["score_range"]
        if min_score <= total_score <= max_score:
            return criteria
    # 默认返回中等绩效评语
    return PERFORMANCE_LEVELS["medium_performance"]




def get_dimension_evaluation(dim_name, score):
    """根据维度名称和分数获取评价内容"""
    evaluations = DIMENSION_EVALUATIONS.get(dim_name)
    if not evaluations:
        return None

    if score >= 8.5:
        return evaluations["high"]
    elif score >= 7.5:
        return evaluations["medium"]
    elif score >= 6.5:
        return evaluations["low"]
    else :
        return evaluations["bad"]



def prepare_report_data(report_data):
    data = report_data.copy()
    performance_eval = get_performance_evaluation(report_data["user_info"]["total_score"])
    data["performance_eval"] = performance_eval
    data["dimension_evaluations"] = {}

    for dim_name, dim_data in data["dimensions"].items():
        score = dim_data["score"]
        eval_data = get_dimension_evaluation(dim_name, score)

        if eval_data:
            # 确保保留原始分数
            original_subs = dim_data["subs"].copy()

            # 处理子维度评价
            for sub_name, sub_score in original_subs.items():
                # 确保sub_score是数值类型
                if not isinstance(sub_score, (int, float)):
                    continue  # 跳过非数值类型

                # 根据子维度分数获取评价级别
                if sub_score >= 8.5:
                    eval_level = "high"
                elif sub_score >= 7.5:
                    eval_level = "medium"
                elif sub_score >= 6.5:
                    eval_level = "low"
                else :
                    eval_level = "bad"

                # 确保子维度评价存在
                if "子维度评价" in eval_data and sub_name in eval_data["子维度评价"]:
                    sub_eval = eval_data["子维度评价"][sub_name]
                    sub_eval["eval_level"] = eval_level

                    # 创建新的子维度数据结构
                    dim_data["subs"][sub_name] = {
                        "score": sub_score,  # 确保保留分数
                        "evaluation": sub_eval
                    }
                else:
                    # 如果没有评价数据，保留原始分数
                    dim_data["subs"][sub_name] = {
                        "score": sub_score,
                        "evaluation": None
                    }

            # 添加大维度评价
            data["dimension_evaluations"][dim_name] = {
                "dimension_eval": eval_data["大维度评价"],
                "eval_level": "high" if score >= 8.5 else "medium" if score >= 7.5 else "low" if score >= 6.5 else "bad"
            }

    # 调试输出
    print("\n====== 数据验证 ======")
    print(f"报告数据中包含维度数: {len(data['dimensions'])}")

    for dim_name, dim_data in data["dimensions"].items():
        print(f"\n维度: {dim_name} (得分: {dim_data['score']})")
        print(f"子维度数量: {len(dim_data['subs'])}")

        for sub_name, sub_data in dim_data["subs"].items():
            # 确保每个子维度都有分数
            if isinstance(sub_data, dict) and 'score' in sub_data:
                print(f"  - {sub_name}: 分数存在 ({sub_data['score']})")
            elif isinstance(sub_data, (int, float)):
                print(f"  - {sub_name}: 基本分数 ({sub_data})")
            else:
                print(f"  - {sub_name}: 无分数数据 ({type(sub_data)})")

    return data


def convert_to_radar_data(report_dimensions):
    """
    将报告数据结构转换为雷达图所需的数据结构

    :param report_dimensions: report_data中的dimensions部分
    :return: 雷达图数据结构
    """
    # 定义雷达图的角度和颜色映射
    group_config = {
        "自我成长与发展": {
            "color": "#00CC00",  # 绿色
            "angles": [0, 30, 60],  # 第一象限
            "sub_order": ["学习与探索动机", "寻求和运用反馈", "情感成熟度"]  # 保持顺序一致
        },
        "管理动力": {
            "color": "#9900FF",  # 紫色
            "angles": [90, 120, 150],  # 第二象限
            "sub_order": ["组织意识", "追求成就", "领导意愿"]
        },
        "管理事务": {
            "color": "#0066FF",  # 蓝色
            "angles": [180, 210, 240],  # 第三象限
            "sub_order": ["跨领域思考", "概念性思维", "适应变化情景"]
        },
        "管理他人": {
            "color": "#FF3333",  # 红色
            "angles": [270, 300, 330],  # 第四象限
            "sub_order": ["人际洞察", "同理心", "发挥他人"]
        }
    }

    radar_data = []

    for group_name, group_data in group_config.items():
        report_group = report_dimensions.get(group_name)
        if not report_group:
            continue

        group_dims = []
        subs = report_group.get('subs', {})

        for idx, sub_name in enumerate(group_data['sub_order']):
            if sub_name in subs:
                angle = group_data['angles'][idx]

                # 提取分数值，兼容数值和字典两种数据结构
                sub_score = subs[sub_name]
                if isinstance(sub_score, dict):
                    # 如果子维度是字典结构，尝试获取score键值
                    score_value = sub_score.get("score", 0)
                elif isinstance(sub_score, (int, float)):
                    # 如果是数值类型，直接使用
                    score_value = sub_score
                else:
                    # 未知类型，默认为0
                    score_value = 0

                group_dims.append({
                    "name": sub_name,
                    "score": score_value,  # 使用提取的数值
                    "angle": angle
                })

        radar_data.append({
            "group": group_name,
            "color": group_data['color'],
            "dims": group_dims
        })

    return radar_data

# def convert_to_radar_data(report_dimensions):
#     """
#     将报告数据结构转换为雷达图所需的数据结构
#
#     :param report_dimensions: report_data中的dimensions部分
#     :return: 雷达图数据结构
#     """
#     # 定义雷达图的角度和颜色映射
#     group_config = {
#         "自我成长与发展": {
#             "color": "#00CC00",  # 绿色
#             "angles": [0, 30, 60],  # 第一象限
#             "sub_order": ["学习与探索动机", "寻求和运用反馈", "情感成熟度"]  # 保持顺序一致
#         },
#         "管理动力": {
#             "color": "#9900FF",  # 紫色
#             "angles": [90, 120, 150],  # 第二象限
#             "sub_order": ["组织意识", "追求成就", "领导意愿"]
#         },
#         "管理事务": {
#             "color": "#0066FF",  # 蓝色
#             "angles": [180, 210, 240],  # 第三象限
#             "sub_order": ["跨领域思考", "概念性思维", "适应变化情景"]
#         },
#         "管理他人": {
#             "color": "#FF3333",  # 红色
#             "angles": [270, 300, 330],  # 第四象限
#             "sub_order": ["人际洞察", "同理心", "发挥他人"]
#         }
#     }
#
#     radar_data = []
#
#     for group_name, group_data in group_config.items():
#         report_group = report_dimensions.get(group_name)
#         if not report_group:
#             continue
#
#         group_dims = []
#         subs = report_group.get('subs', {})
#
#         for idx, sub_name in enumerate(group_data['sub_order']):
#             if sub_name in subs:
#                 angle = group_data['angles'][idx]
#                 score = subs[sub_name]
#                 group_dims.append({
#                     "name": sub_name,
#                     "score": score,
#                     "angle": angle
#                 })
#
#         radar_data.append({
#             "group": group_name,
#             "color": group_data['color'],
#             "dims": group_dims
#         })
#
#     return radar_data


# 文件名清理函数
def sanitize_filename(name):
    """
    清理文件名中的非法字符

    :param name: 原始名称
    :return: 安全可用的文件名
    """
    # 规范化Unicode字符
    if not name:
        return "unknown"

    name = unicodedata.normalize('NFKC', name)

    # 替换特殊字符为下划线
    name = re.sub(r'[\\/*?:"<>|]', '_', name)

    # 移除首尾空格
    name = name.strip()

    # 如果名字为空，使用默认值
    if not name:
        name = "unknown"

    return name


# 文件名生成函数
def generate_filename(prefix, user_name, extension="png", with_timestamp=True):
    """
    生成个性化文件名
    :param prefix: 文件名前缀，如"radar_chart"
    :param user_name: 用户名
    :param extension: 文件扩展名
    :param with_timestamp: 是否包含时间戳
    :return: 安全可用的文件名
    """
    # 清理用户名
    safe_name = sanitize_filename(user_name)
    # 生成基本文件名
    filename = f"{prefix}_{safe_name}"
    # 添加时间戳
    if with_timestamp:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename += f"_{timestamp}"
    # 添加扩展名
    filename += f".{extension}"
    return filename

# def generate_report(data, template_path='assets/report_template.html'):
#
#     radar_data = convert_to_radar_data(report_data['dimensions'])
#     # 生成个性化雷达图文件名
#     user_name = report_data['user_info']['name']
#     chart_filename = generate_filename("radar_chart", user_name)
#     chart_path = os.path.join('assets', chart_filename)
#     output_filename = generate_filename("report", user_name, extension="pdf" , with_timestamp=False)
#     output_path = os.path.join('output', output_filename)
#     print(f"生成的雷达图路径: {chart_path}")
#     generated_path = radar_chart.generate_radar_chart(radar_data, chart_path)
#     # 设置Jinja2环境
#     env = Environment(loader=FileSystemLoader('.'))
#     template = env.get_template(template_path)
#
#     enriched_data = prepare_report_data(data)
#
#     # 嵌入图片为Base64
#     with open(generated_path, "rb") as image_file:
#         encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
#     chart_base64 = f"data:image/png;base64,{encoded_string}"
#
#     # 渲染HTML内容
#     html_out = template.render(chart_img=chart_base64, **enriched_data)
#
#     # 保存调试HTML文件
#     # with open("debug.html", "w", encoding="utf-8") as f:
#     #     f.write(html_out)
#
#     # 使用WeasyPrint生成PDF - 保持简洁
#     HTML(string=html_out).write_pdf(output_path)
#     print(f"PDF报告已生成: {output_path}")


def get_dim_strengths(strengths):
    """获取所有优势维度"""
    return strengths.get("维度", [])

def get_sub_strengths(strengths):
    """获取所有优势子维度"""
    return strengths.get("子维度", [])

# 在报告中显示劣势维度的过滤器
def get_dim_weaknesses(weaknesses):
    """获取所有劣势维度"""
    return weaknesses.get("维度", [])

def get_sub_weaknesses(weaknesses):
    """获取所有劣势子维度"""
    return weaknesses.get("子维度", [])


def get_top_strength(strengths):
    """获取最显著的优势维度或子维度"""
    candidates = strengths.get("维度", []) + strengths.get("子维度", [])
    if not candidates:
        return None

    # 按差异值从大到小排序
    candidates.sort(key=lambda x: x["diff"], reverse=True)
    return candidates[0]


def get_main_weakness(weaknesses):
    """获取最显著的劣势维度或子维度"""
    candidates = weaknesses.get("维度", []) + weaknesses.get("子维度", [])
    if not candidates:
        return None

    # 按差异值从小到大排序（差异值越小说明越需要关注）
    candidates.sort(key=lambda x: x["diff"])
    return candidates[0]

def batch_generate_reports(excel_path, output_dir="output", assets_dir="assets"):
    """
    批量生成人才报告
    :param excel_path: Excel文件路径
    :param output_dir: 报告输出目录
    :param assets_dir: 资源文件目录
    """
    # 确保目录存在
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(assets_dir, exist_ok=True)

    # 读取Excel数据
    print(f"读取Excel数据: {excel_path}")
    report_data_list, average_scores = read_excel_with_averages(excel_path)

    # 批量生成报告
    print(f"开始批量生成报告 (共{len(report_data_list)}份)")
    for i, report_data in enumerate(tqdm(report_data_list, desc="生成报告")):
        try:
            user_name = report_data['user_info']['name']
            report_data = prepare_report_data(report_data)
            report_data = compare_with_average(report_data, average_scores)

            # 生成雷达图
            radar_data = convert_to_radar_data(report_data['dimensions'])
            chart_filename = generate_filename("radar_chart", user_name)
            chart_path = os.path.join(assets_dir, chart_filename)
            generated_path = radar_chart.generate_radar_chart(radar_data, chart_path)

            # 设置Jinja2环境
            env = Environment(loader=FileSystemLoader('.'))
            env.filters['get_dim_strengths'] = get_dim_strengths
            env.filters['get_dim_weaknesses'] = get_dim_weaknesses
            env.filters['get_sub_strengths'] = get_sub_strengths
            env.filters['get_sub_weaknesses'] = get_sub_weaknesses
            env.filters['get_top_strength'] = get_top_strength
            env.filters['get_main_weakness'] = get_main_weakness

            template = env.get_template('assets/report_template.html')

            # 嵌入图片为Base64
            with open(generated_path, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
            chart_base64 = f"data:image/png;base64,{encoded_string}"

            # 渲染HTML内容
            html_out = template.render(**report_data, chart_img=chart_base64)

            # 生成PDF报告
            report_filename = generate_filename("管理潜质测评报告", user_name, extension="pdf", with_timestamp=False)
            report_path = os.path.join(output_dir, report_filename)
            HTML(string=html_out).write_pdf(report_path)

        except Exception as e:
            print(f"生成 {user_name} 的报告时出错: {str(e)}")
            # 打印详细错误信息
            import traceback
            traceback.print_exc()

    print(f"\n报告生成完成，保存在: {output_dir}")


if __name__ == '__main__':
    # 生成报告
    # generate_report(report_data)
    # 指定Excel文件路径
    excel_path = "data.xlsx"  # 请确保Excel文件存在
    # 批量生成报告
    batch_generate_reports(excel_path)
# 通用化报告生成系统

## 概述

通用化报告生成系统是一个支持多种试卷报告生成的灵活框架，通过配置文件驱动，可以轻松适配不同的测评试卷，生成个性化的PDF报告。

## 系统特点

- **配置驱动**: 通过YAML配置文件定义试卷结构、评价内容、分数区间等
- **多试卷支持**: 支持不同试卷的维度结构、评价体系和报告模板
- **灵活扩展**: 新增试卷只需创建配置文件，无需修改核心代码
- **智能评价**: 根据分数自动匹配评价级别和个性化内容
- **可视化图表**: 自动生成雷达图等可视化内容
- **批量处理**: 支持Excel数据批量生成报告

## 系统架构

```
generators/
├── configs/                    # 配置文件目录
│   ├── 1.yaml                 # 管理潜质测评配置
│   ├── 2.yaml                 # 商业推理能力配置
│   └── ...                    # 其他试卷配置
├── templates/                  # 报告模板目录
│   ├── management_potential_template.html
│   ├── business_reasoning_template.html
│   └── ...
├── config_loader.py           # 配置加载器
├── report_core.py             # 报告生成核心
├── radar_chart.py             # 雷达图生成器
└── test_universal_system.py   # 测试脚本
```

## 配置文件结构

### 基本信息
```yaml
paper_id: 1                    # 试卷ID
paper_name: "管理潜质测评"      # 试卷名称
paper_description: "..."        # 试卷描述
paper_version: "v1.0"          # 版本号
```

### 字段映射
```yaml
field_mapping:
  姓名: "name"                  # Excel列名到内部字段的映射
  总分: "total_score"
  大维度1：自我成长与发展: "自我成长与发展"
  # ...
```

### 维度结构
```yaml
dimensions:
  - name: "自我成长与发展"      # 大维度名称
    color: "#00CC00"           # 雷达图颜色
    description: "..."          # 维度描述
    radar_angles: [0, 30, 60]  # 雷达图角度
    sub_dimensions:             # 子维度列表
      - name: "学习与探索动机"
        description: "..."
      # ...
```

### 分数区间
```yaml
score_levels:
  - name: "高潜力"              # 等级名称
    min: 8.5                   # 最低分
    max: 10.0                  # 最高分
    summary: "..."              # 等级总结
    development_focus: "..."    # 发展重点
    color: "#4CAF50"           # 等级颜色
```

### 维度评价
```yaml
dimension_evaluations:
  自我成长与发展:
    high:                       # 高等级评价
      dimension_eval: "..."     # 维度评价
      sub_dimensions:           # 子维度评价
        学习与探索动机:
          潜质特点: "..."
          工作中的倾向: "..."
    medium:                     # 中等评价
      # ...
    low:                        # 低等评价
      # ...
    bad:                        # 差等评价
      # ...
```

## 使用方法

### 1. 创建新试卷配置

1. 在 `configs/` 目录下创建新的YAML配置文件
2. 按照配置文件结构定义试卷信息
3. 创建对应的报告模板（可选）

### 2. 准备数据

Excel文件应包含以下列：
- 姓名
- 总分
- 各维度分数
- 各子维度分数

### 3. 生成报告

```python
from report_core import UniversalReportGenerator

# 创建报告生成器
generator = UniversalReportGenerator()

# 批量生成报告
generator.batch_generate_reports(
    excel_path='data.xlsx',
    paper_id=1,
    output_dir='output'
)
```

### 4. 单个报告生成

```python
from report_core import generate_single_report

# 准备用户数据
user_data = {
    "user_info": {
        "name": "张三",
        "total_score": 8.2
    },
    "dimensions": {
        "自我成长与发展": {
            "score": 8.5,
            "subs": {
                "学习与探索动机": 8.8,
                "寻求和运用反馈": 8.3,
                "情感成熟度": 8.4
            }
        }
        # ... 其他维度
    }
}

# 生成报告
generate_single_report(
    paper_id=1,
    user_data=user_data,
    output_path='output/张三_报告.pdf'
)
```

## 测试系统

运行测试脚本验证系统功能：

```bash
cd backend/reports/generators
python test_universal_system.py
```

测试内容包括：
- 配置加载功能
- 字段映射功能
- 分数区间功能
- 维度评价功能
- 配置验证功能
- 测试数据创建
- 报告生成功能

## 扩展指南

### 添加新试卷

1. **创建配置文件**
   ```yaml
   # configs/3.yaml
   paper_id: 3
   paper_name: "新试卷名称"
   # ... 其他配置
   ```

2. **定义维度结构**
   ```yaml
   dimensions:
     - name: "维度1"
       color: "#FF0000"
       sub_dimensions:
         - name: "子维度1"
         # ...
   ```

3. **设置分数区间**
   ```yaml
   score_levels:
     - name: "优秀"
       min: 8.5
       max: 10.0
       # ...
   ```

4. **编写评价内容**
   ```yaml
   dimension_evaluations:
     维度1:
       high:
         dimension_eval: "..."
         sub_dimensions:
           子维度1:
             潜质特点: "..."
             工作中的倾向: "..."
   ```

### 自定义报告模板

1. 在 `templates/` 目录下创建HTML模板
2. 使用Jinja2语法定义模板变量
3. 在配置文件中指定模板名称

```yaml
template:
  name: "custom_template.html"
  title: "自定义报告标题"
  description: "报告描述"
```

## 注意事项

1. **配置文件格式**: 确保YAML格式正确，缩进一致
2. **字段映射**: Excel列名必须与配置文件中的字段映射一致
3. **分数范围**: 确保分数在合理范围内（通常0-10）
4. **模板兼容**: 报告模板需要与数据结构匹配
5. **依赖安装**: 确保安装了所需的Python包

## 依赖包

```bash
pip install pyyaml pandas openpyxl jinja2 weasyprint matplotlib
```

## 故障排除

### 常见问题

1. **配置文件加载失败**
   - 检查YAML格式是否正确
   - 确认文件路径是否正确
   - 验证必需字段是否完整

2. **数据读取错误**
   - 检查Excel文件格式
   - 确认字段映射是否正确
   - 验证数据列是否存在

3. **报告生成失败**
   - 检查模板文件是否存在
   - 确认数据结构是否匹配
   - 验证输出目录权限

4. **雷达图生成错误**
   - 检查维度配置是否正确
   - 确认角度设置是否合理
   - 验证颜色值格式

## 更新日志

### v1.0.0
- 初始版本发布
- 支持管理潜质测评和商业推理能力
- 实现配置驱动的报告生成
- 支持批量处理和单个报告生成
- 集成雷达图可视化功能 
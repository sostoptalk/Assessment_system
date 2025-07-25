# YAML配置导入工具使用说明

此工具用于将现有的YAML配置文件导入到数据库的`report_templates`表中。

## 前提条件

1. 确保已安装必要的Python包：
   ```
   pip install pyyaml sqlalchemy pymysql
   ```

2. 确保数据库连接信息正确
   - 脚本将自动创建`report_templates`表（如果不存在）

## 使用方法

### 基本用法

切换到scripts目录，运行导入脚本：

```bash
cd backend/scripts
python import_yaml_templates.py --db-host localhost --db-user root --db-password password --db-name assessment
```

或者修改并使用提供的shell脚本：

```bash
# 先修改脚本中的数据库连接信息
nano import_yaml_configs.sh
# 然后运行脚本
bash import_yaml_configs.sh
```

这将默认导入`../reports/generators/configs`目录下的所有YAML文件，并使用文件名作为`paper_id`（例如，`10.yaml`对应`paper_id=10`）。

### 指定YAML目录

如果YAML文件位于其他目录，可以使用`--yaml-dir`参数指定：

```bash
python import_yaml_templates.py --yaml-dir "/path/to/your/yaml/files"
```

### 指定YAML文件到paper_id的映射

如果YAML文件名与`paper_id`不一致，可以使用`--mapping`参数指定映射关系：

```bash
python import_yaml_templates.py --mapping "config1.yaml:10,config2.yaml:16"
```

上述命令将`config1.yaml`映射到`paper_id=10`，将`config2.yaml`映射到`paper_id=16`。

## 示例

假设项目目录结构如下：

```
/backend
  /reports
    /generators
      /configs
        10.yaml
        16.yaml
  /scripts
    import_yaml_templates.py
```

### 示例1：导入所有配置

```bash
cd backend/scripts
bash import_yaml_configs.sh
```

### 示例2：导入指定目录的配置

```bash
python import_yaml_templates.py --yaml-dir "../reports/generators/configs" \
  --db-host localhost --db-user root --db-password password --db-name assessment
```

### 示例3：使用自定义映射

```bash
python import_yaml_templates.py --mapping "10.yaml:10,16.yaml:16" \
  --db-host localhost --db-user root --db-password password --db-name assessment
```

## 注意事项

1. 如果数据库中已存在相同`paper_id`的模板，脚本将更新现有记录而不是创建新记录
2. 脚本会自动将YAML内容转换为JSON格式并同时存储两种格式
3. 默认模板名称为"试卷{paper_id}报告模板"，可以在导入后通过Web界面修改
4. 确保YAML文件格式正确，否则导入可能失败
5. 本脚本直接定义了数据库模型，不依赖于主应用，避免了导入主应用可能引起的路径问题

## 错误排查

1. **数据库连接错误**：检查提供的数据库连接信息是否正确
2. **包缺失错误**：确保已安装`pyyaml`、`sqlalchemy`和`pymysql`包
3. **YAML解析错误**：检查YAML文件格式是否符合规范 
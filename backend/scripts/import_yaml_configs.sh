#!/bin/bash

# 导入YAML配置示例脚本
cd "$(dirname "$0")"

echo "开始导入YAML配置文件..."

# 设置数据库连接信息 - 请根据实际情况修改
DB_HOST="localhost"
DB_USER="root"
DB_PASSWORD="Yrui2997"
DB_NAME="test_assessment"

# 运行Python导入脚本
python import_yaml_templates.py \
  --db-host "$DB_HOST" \
  --db-user "$DB_USER" \
  --db-password "$DB_PASSWORD" \
  --db-name "$DB_NAME"

echo "YAML配置导入完成！" 
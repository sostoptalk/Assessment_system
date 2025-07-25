#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import yaml
import json
import asyncio
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import argparse
import glob

# 添加项目根目录到路径，使其能够导入项目模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 创建Base类和数据库连接
Base = declarative_base()

# 直接定义ReportTemplate模型，避免导入主应用
class ReportTemplate(Base):
    __tablename__ = "report_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    paper_id = Column(Integer, nullable=False, index=True)
    config = Column(Text, nullable=True)  # 存储JSON格式的配置
    yaml_config = Column(Text, nullable=True)  # 存储YAML格式的配置
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

# 获取数据库URL函数
def get_db_url():
    # 从环境变量获取，如果没有则使用默认值
    db_host = os.environ.get("DB_HOST", "localhost")
    db_user = os.environ.get("DB_USER", "root")
    db_password = os.environ.get("DB_PASSWORD", "password")
    db_name = os.environ.get("DB_NAME", "assessment")
    
    return f"mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}"

def yaml_to_json(yaml_str):
    """将YAML字符串转换为JSON字符串"""
    try:
        yaml_dict = yaml.safe_load(yaml_str)
        return json.dumps(yaml_dict, ensure_ascii=False)
    except Exception as e:
        print(f"YAML转换失败: {str(e)}")
        return None

async def import_yaml_files(yaml_dir, paper_id_map=None):
    """
    导入指定目录下的所有YAML文件到数据库
    
    Args:
        yaml_dir: YAML文件所在目录
        paper_id_map: 可选，YAML文件名到paper_id的映射字典，格式如 {'10.yaml': 10}
                     如果不提供，将使用文件名作为paper_id
    """
    # 获取数据库连接
    engine = create_engine(get_db_url())
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # 查找所有YAML文件
        yaml_files = glob.glob(os.path.join(yaml_dir, "*.yaml"))
        if not yaml_files:
            print(f"警告: 在 {yaml_dir} 中未找到YAML文件")
            return
            
        for yaml_file in yaml_files:
            file_name = os.path.basename(yaml_file)
            print(f"处理文件: {file_name}")
            
            # 确定paper_id
            if paper_id_map and file_name in paper_id_map:
                paper_id = paper_id_map[file_name]
            else:
                # 默认使用文件名作为paper_id (去掉.yaml扩展名)
                try:
                    paper_id = int(os.path.splitext(file_name)[0])
                except ValueError:
                    print(f"警告: 无法从文件名 {file_name} 确定paper_id，跳过此文件")
                    continue
            
            # 读取YAML文件
            with open(yaml_file, 'r', encoding='utf-8') as f:
                yaml_content = f.read()
            
            # 将YAML转换为JSON
            json_content = yaml_to_json(yaml_content)
            if not json_content:
                print(f"跳过文件 {file_name}: YAML转换失败")
                continue
                
            # 检查是否已存在相同paper_id的模板
            existing_template = db.query(ReportTemplate).filter(
                ReportTemplate.paper_id == paper_id
            ).first()
            
            if existing_template:
                print(f"更新paper_id={paper_id}的现有模板")
                existing_template.yaml_config = yaml_content
                existing_template.config = json_content
                existing_template.updated_at = datetime.now()
            else:
                # 创建新模板
                template_name = f"试卷{paper_id}报告模板"
                new_template = ReportTemplate(
                    name=template_name,
                    paper_id=paper_id,
                    yaml_config=yaml_content,
                    config=json_content,
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )
                db.add(new_template)
                print(f"添加paper_id={paper_id}的新模板")
            
            # 提交更改
            db.commit()
            
        print("YAML导入完成!")
        
    except Exception as e:
        print(f"导入过程中出错: {str(e)}")
        db.rollback()
    finally:
        db.close()

def main():
    parser = argparse.ArgumentParser(description='导入YAML模板文件到数据库')
    parser.add_argument('--yaml-dir', type=str, default='../reports/generators/configs',
                        help='YAML配置文件的目录路径，默认为 ../reports/generators/configs')
    parser.add_argument('--mapping', type=str, help='可选的YAML文件名到paper_id的映射，格式为: "10.yaml:10,16.yaml:16"')
    
    # 数据库连接参数
    parser.add_argument('--db-host', type=str, help='数据库主机名')
    parser.add_argument('--db-user', type=str, help='数据库用户名')
    parser.add_argument('--db-password', type=str, help='数据库密码')
    parser.add_argument('--db-name', type=str, help='数据库名称')
    
    args = parser.parse_args()
    
    # 设置环境变量
    if args.db_host:
        os.environ["DB_HOST"] = args.db_host
    if args.db_user:
        os.environ["DB_USER"] = args.db_user
    if args.db_password:
        os.environ["DB_PASSWORD"] = args.db_password
    if args.db_name:
        os.environ["DB_NAME"] = args.db_name
    
    # 转换映射参数
    paper_id_map = None
    if args.mapping:
        paper_id_map = {}
        mappings = args.mapping.split(',')
        for mapping in mappings:
            parts = mapping.strip().split(':')
            if len(parts) == 2:
                paper_id_map[parts[0].strip()] = int(parts[1].strip())
    
    # 运行导入
    asyncio.run(import_yaml_files(args.yaml_dir, paper_id_map))

if __name__ == "__main__":
    main() 
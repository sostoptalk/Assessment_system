#!/usr/bin/env python3
"""
冗余路径清理脚本

确保所有文件从旧路径 backend/backend/reports 迁移到新路径 backend/reports，然后删除旧路径。
"""

import os
import shutil
from pathlib import Path
import sys
import time
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

def migrate_files(source_dir, target_dir, file_pattern="*.*", delete_source=False):
    """将文件从源目录迁移到目标目录
    
    Args:
        source_dir: 源目录
        target_dir: 目标目录
        file_pattern: 文件匹配模式
        delete_source: 是否删除源文件
        
    Returns:
        迁移的文件数量
    """
    if not source_dir.exists():
        logger.info(f"源目录不存在: {source_dir}")
        return 0
        
    if not target_dir.exists():
        logger.info(f"创建目标目录: {target_dir}")
        target_dir.mkdir(parents=True, exist_ok=True)
        
    count = 0
    for file in source_dir.glob(file_pattern):
        if file.is_file():
            target_file = target_dir / file.name
            if not target_file.exists():
                logger.info(f"复制 {file.name} 到 {target_dir}")
                shutil.copy2(file, target_file)
                count += 1
            else:
                logger.debug(f"目标文件已存在，比较内容: {target_file}")
                # 比较文件大小和修改时间
                if (file.stat().st_size != target_file.stat().st_size or
                    file.stat().st_mtime > target_file.stat().st_mtime):
                    logger.info(f"源文件更新，备份并覆盖: {target_file}")
                    # 备份现有文件
                    backup_file = target_dir / f"{file.stem}.bak_{int(time.time())}{file.suffix}"
                    shutil.copy2(target_file, backup_file)
                    # 复制新文件
                    shutil.copy2(file, target_file)
                    count += 1
                else:
                    logger.debug(f"文件相同，跳过: {file.name}")
            
            # 如果需要删除源文件
            if delete_source:
                logger.info(f"删除源文件: {file}")
                file.unlink()
    
    return count

def remove_directory_if_empty(directory):
    """如果目录为空，则删除它
    
    Args:
        directory: 目录路径
    
    Returns:
        是否删除了目录
    """
    if not directory.exists():
        return False
    
    # 检查目录是否为空
    if not any(directory.iterdir()):
        logger.info(f"删除空目录: {directory}")
        directory.rmdir()
        return True
    else:
        logger.info(f"目录不为空，保留: {directory}")
        return False

def cleanup_directory(directory):
    """递归删除空目录
    
    Args:
        directory: 目录路径
    """
    if not directory.exists():
        return
    
    # 首先递归处理所有子目录
    for item in directory.iterdir():
        if item.is_dir():
            cleanup_directory(item)
    
    # 然后尝试删除当前目录（如果为空）
    remove_directory_if_empty(directory)

def main():
    """主函数"""
    # 获取当前脚本所在目录
    script_dir = Path(__file__).parent.absolute()
    logger.info(f"当前脚本目录: {script_dir}")
    
    # 定义源目录和目标目录
    source_base = script_dir / "backend" / "reports"
    target_base = script_dir / "reports"
    
    if not source_base.exists():
        logger.info(f"旧路径不存在，无需清理: {source_base}")
        return
    
    # 确保目标目录存在
    if not target_base.exists():
        target_base.mkdir(parents=True, exist_ok=True)
        logger.info(f"创建了目标目录: {target_base}")
    
    # 开始迁移
    logger.info("开始迁移文件...")
    
    # 迁移配置文件
    source_configs = source_base / "generators" / "configs"
    target_configs = target_base / "generators" / "configs"
    config_count = migrate_files(source_configs, target_configs, "*.yaml", delete_source=True)
    
    # 迁移模板文件
    source_templates = source_base / "generators" / "templates"
    target_templates = target_base / "generators" / "templates"
    template_count = migrate_files(source_templates, target_templates, "*.html", delete_source=True)
    
    # 迁移其他文件
    other_count = 0
    for pattern in ["*.py", "*.json", "*.md", "*.txt"]:
        source_generators = source_base / "generators"
        target_generators = target_base / "generators"
        other_count += migrate_files(source_generators, target_generators, pattern, delete_source=True)
    
    # 迁移assets文件夹中的内容
    source_assets = source_base / "generators" / "assets"
    target_assets = target_base / "generators" / "assets"
    assets_count = 0
    if source_assets.exists():
        for pattern in ["*.png", "*.jpg", "*.jpeg", "*.svg", "*.gif"]:
            assets_count += migrate_files(source_assets, target_assets, pattern, delete_source=True)
    
    # 递归删除空目录
    logger.info("开始清理空目录...")
    cleanup_directory(source_base)
    
    logger.info(f"\n迁移完成:")
    logger.info(f"- 迁移了 {config_count} 个配置文件")
    logger.info(f"- 迁移了 {template_count} 个模板文件")
    logger.info(f"- 迁移了 {assets_count} 个资源文件")
    logger.info(f"- 迁移了 {other_count} 个其他文件")
    logger.info(f"\n新的配置路径: {target_configs}")
    logger.info(f"新的模板路径: {target_templates}")

if __name__ == "__main__":
    main() 
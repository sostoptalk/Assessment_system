#!/usr/bin/env python3
"""
配置文件路径迁移脚本

将配置文件从 backend/backend/reports 移动到 backend/reports 目录。
"""

import os
import shutil
from pathlib import Path
import sys
import time

def migrate_files(source_dir, target_dir, file_pattern="*.*"):
    """将文件从源目录迁移到目标目录
    
    Args:
        source_dir: 源目录
        target_dir: 目标目录
        file_pattern: 文件匹配模式
        
    Returns:
        迁移的文件数量
    """
    if not source_dir.exists():
        print(f"源目录不存在: {source_dir}")
        return 0
        
    if not target_dir.exists():
        print(f"创建目标目录: {target_dir}")
        target_dir.mkdir(parents=True, exist_ok=True)
        
    count = 0
    for file in source_dir.glob(file_pattern):
        if file.is_file():
            target_file = target_dir / file.name
            if not target_file.exists():
                print(f"复制 {file.name} 到 {target_dir}")
                shutil.copy2(file, target_file)
                count += 1
            else:
                print(f"目标文件已存在，比较内容: {target_file}")
                # 比较文件大小和修改时间
                if (file.stat().st_size != target_file.stat().st_size or
                    file.stat().st_mtime > target_file.stat().st_mtime):
                    print(f"源文件更新，备份并覆盖: {target_file}")
                    # 备份现有文件
                    backup_file = target_dir / f"{file.stem}.bak_{int(time.time())}{file.suffix}"
                    shutil.copy2(target_file, backup_file)
                    # 复制新文件
                    shutil.copy2(file, target_file)
                    count += 1
                else:
                    print(f"文件相同，跳过: {file.name}")
    
    return count

def main():
    """主函数"""
    # 获取当前脚本所在目录
    script_dir = Path(__file__).parent.absolute()
    print(f"当前脚本目录: {script_dir}")
    
    # 定义源目录和目标目录
    source_base = script_dir / "backend" / "reports"
    target_base = script_dir / "reports"
    
    # 迁移配置文件
    source_configs = source_base / "generators" / "configs"
    target_configs = target_base / "generators" / "configs"
    config_count = migrate_files(source_configs, target_configs, "*.yaml")
    
    # 迁移模板文件
    source_templates = source_base / "generators" / "templates"
    target_templates = target_base / "generators" / "templates"
    template_count = migrate_files(source_templates, target_templates, "*.html")
    
    # 迁移其他文件
    for pattern in ["*.py", "*.json"]:
        source_generators = source_base / "generators"
        target_generators = target_base / "generators"
        migrate_files(source_generators, target_generators, pattern)
    
    print(f"\n迁移完成:")
    print(f"- 迁移了 {config_count} 个配置文件")
    print(f"- 迁移了 {template_count} 个模板文件")
    print(f"\n新的配置路径: {target_configs}")
    print(f"新的模板路径: {target_templates}")

if __name__ == "__main__":
    main() 
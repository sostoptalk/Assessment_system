import yaml
import os
from typing import Dict, List, Optional, Any
from pathlib import Path

class PaperConfigLoader:
    """试卷配置加载器 - 用于读取和管理不同试卷的配置文件"""
    
    def __init__(self, config_dir: str = "configs"):
        # 获取当前文件所在目录
        current_dir = Path(__file__).parent
        self.config_dir = current_dir / config_dir
        self._configs_cache = {}
        
    def load_config(self, paper_id: int) -> Dict[str, Any]:
        """加载指定试卷的配置文件"""
        if paper_id in self._configs_cache:
            return self._configs_cache[paper_id]
            
        config_file = self.config_dir / f"{paper_id}.yaml"
        
        if not config_file.exists():
            raise FileNotFoundError(f"配置文件不存在: {config_file}")
            
        print(f"正在加载配置文件: {config_file}")
            
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                
            self._validate_config(config)
            self._configs_cache[paper_id] = config
            return config
            
        except yaml.YAMLError as e:
            raise yaml.YAMLError(f"配置文件格式错误 {config_file}: {e}")
            
    def get_available_papers(self) -> List[Dict[str, Any]]:
        """获取所有可用的试卷配置信息"""
        papers = []
        
        for config_file in self.config_dir.glob("*.yaml"):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f)
                    
                if self._is_valid_paper_config(config):
                    papers.append({
                        'paper_id': config.get('paper_id'),
                        'paper_name': config.get('paper_name'),
                        'paper_description': config.get('paper_description'),
                        'paper_version': config.get('paper_version'),
                        'dimensions_count': len(config.get('dimensions', [])),
                        'config_file': config_file.name
                    })
                    
            except Exception as e:
                print(f"警告: 无法读取配置文件 {config_file}: {e}")
                continue
                
        return sorted(papers, key=lambda x: x['paper_id'])
        
    def get_dimension_names(self, paper_id: int) -> List[str]:
        """获取试卷的维度名称列表"""
        config = self.load_config(paper_id)
        return [dim['name'] for dim in config.get('dimensions', [])]
        
    def get_score_level(self, paper_id: int, score: float) -> Optional[Dict[str, Any]]:
        """根据分数获取对应的分数区间配置"""
        config = self.load_config(paper_id)
        
        for level in config.get('score_levels', []):
            if level['min'] <= score <= level['max']:
                return level
                
        return None
        
    def get_dimension_evaluation(self, paper_id: int, dimension_name: str, score: float) -> Optional[Dict[str, Any]]:
        """获取维度评价内容"""
        config = self.load_config(paper_id)
        
        level = self._get_evaluation_level(score)
        if not level:
            return None
            
        dimension_evaluations = config.get('dimension_evaluations', {})
        if dimension_name not in dimension_evaluations:
            return None
            
        return dimension_evaluations[dimension_name].get(level)
        
    def get_field_mapping(self, paper_id: int) -> Dict[str, str]:
        """获取字段映射配置"""
        config = self.load_config(paper_id)
        return config.get('field_mapping', {})
        
    def get_radar_chart_config(self, paper_id: int) -> Dict[str, Any]:
        """获取雷达图配置"""
        config = self.load_config(paper_id)
        return config.get('radar_chart', {})
        
    def get_template_config(self, paper_id: int) -> Dict[str, Any]:
        """获取模板配置"""
        config = self.load_config(paper_id)
        return config.get('template', {})
        
    def _validate_config(self, config: Dict[str, Any]) -> None:
        """验证配置文件的完整性"""
        required_fields = ['paper_id', 'paper_name', 'dimensions', 'score_levels']
        
        for field in required_fields:
            if field not in config:
                raise ValueError(f"配置文件缺少必需字段: {field}")
                
        for dimension in config['dimensions']:
            if 'name' not in dimension:
                raise ValueError("维度配置缺少name字段")
            if 'sub_dimensions' not in dimension:
                raise ValueError(f"维度 {dimension['name']} 缺少sub_dimensions字段")
                
        for level in config['score_levels']:
            required_level_fields = ['name', 'min', 'max', 'summary', 'development_focus']
            for field in required_level_fields:
                if field not in level:
                    raise ValueError(f"分数区间配置缺少必需字段: {field}")
                    
    def _is_valid_paper_config(self, config: Dict[str, Any]) -> bool:
        """检查是否为有效的试卷配置"""
        try:
            self._validate_config(config)
            return True
        except ValueError:
            return False
            
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
            
    def clear_cache(self) -> None:
        """清空配置缓存"""
        self._configs_cache.clear()

# 全局配置加载器实例
config_loader = PaperConfigLoader()

def get_paper_config(paper_id: int) -> Dict[str, Any]:
    """获取试卷配置的便捷函数"""
    return config_loader.load_config(paper_id)

def get_available_papers() -> List[Dict[str, Any]]:
    """获取所有可用试卷的便捷函数"""
    return config_loader.get_available_papers() 
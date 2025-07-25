-- 修改report_templates表，添加html_content字段
ALTER TABLE `report_templates` 
ADD COLUMN `html_content` TEXT COMMENT '模板HTML内容' AFTER `yaml_config`;

-- 创建索引
CREATE INDEX `idx_report_templates_paper_id` ON `report_templates` (`paper_id`);

-- 更新注释
ALTER TABLE `report_templates` 
MODIFY COLUMN `name` VARCHAR(200) NOT NULL COMMENT '模板名称',
MODIFY COLUMN `config` JSON NOT NULL COMMENT '模板配置（JSON格式，包含组件、样式等）',
MODIFY COLUMN `yaml_config` TEXT NOT NULL COMMENT '模板配置（YAML格式，包含评分标准、维度定义等）'; 
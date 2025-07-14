-- 为questions表添加选项乱序字段
ALTER TABLE `questions` 
ADD COLUMN `shuffle_options` BOOLEAN DEFAULT FALSE COMMENT '是否启用选项乱序';

-- 为paper_assignments表添加选项乱序相关字段
ALTER TABLE `paper_assignments` 
ADD COLUMN `option_orders` JSON DEFAULT NULL COMMENT '该用户本次测试的选项顺序，存储为JSON对象，格式：{question_id: [option_indices]}';

-- 添加索引以提高查询性能
CREATE INDEX `idx_questions_shuffle_options` ON `questions` (`shuffle_options`); 
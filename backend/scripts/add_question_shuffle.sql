-- 为paper_questions表添加乱序相关字段
ALTER TABLE `paper_questions` 
ADD COLUMN `is_shuffled` BOOLEAN DEFAULT FALSE COMMENT '是否启用题目乱序',
ADD COLUMN `shuffle_seed` INT DEFAULT NULL COMMENT '乱序种子，用于生成随机顺序',
ADD COLUMN `shuffled_order` JSON DEFAULT NULL COMMENT '乱序后的题目顺序，存储为JSON数组';

-- 为paper_assignments表添加乱序相关字段
ALTER TABLE `paper_assignments` 
ADD COLUMN `question_order` JSON DEFAULT NULL COMMENT '该用户本次测试的题目顺序，存储为JSON数组';

-- 添加索引以提高查询性能
CREATE INDEX `idx_paper_questions_shuffled` ON `paper_questions` (`paper_id`, `is_shuffled`);
CREATE INDEX `idx_paper_assignments_order` ON `paper_assignments` (`paper_id`, `user_id`); 
-- 数据库初始化脚本
-- 适用于人才测评平台
-- 请先创建数据库（如 test_assessment），再执行本脚本

-- 1. 用户表
CREATE TABLE IF NOT EXISTS users (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '用户唯一ID',
    username VARCHAR(50) NOT NULL UNIQUE COMMENT '用户名（登录用）',
    password_hash VARCHAR(255) NOT NULL COMMENT '加密后的密码',
    real_name VARCHAR(50) COMMENT '真实姓名',
    role ENUM('admin','participant') NOT NULL COMMENT '角色（管理员/被试者）',
    email VARCHAR(100) COMMENT '邮箱',
    phone VARCHAR(20) COMMENT '手机号',
    is_active BOOLEAN DEFAULT 1 COMMENT '是否激活',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户表';

-- 2. 题库表
CREATE TABLE IF NOT EXISTS questions (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '题目ID',
    content TEXT NOT NULL COMMENT '题干',
    type ENUM('single','multiple','indefinite') NOT NULL COMMENT '题型',
    options JSON NOT NULL COMMENT '选项及分数（JSON）',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='题库表';

-- 3. 答卷表
CREATE TABLE IF NOT EXISTS answers (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '答卷ID',
    user_id INT NOT NULL COMMENT '被试者ID',
    question_id INT NOT NULL COMMENT '题目ID',
    answer JSON NOT NULL COMMENT '答案（如["A"]或["A","C"]）',
    score FLOAT COMMENT '本题得分',
    answered_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '答题时间',
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (question_id) REFERENCES questions(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='答卷表';

-- 4. 报告表
CREATE TABLE IF NOT EXISTS reports (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '报告ID',
    user_id INT NOT NULL COMMENT '被试者ID',
    pdf_path VARCHAR(255) NOT NULL COMMENT 'PDF文件存储路径',
    status ENUM('pending','generated','failed') DEFAULT 'pending' COMMENT '报告状态',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '生成时间',
    FOREIGN KEY (user_id) REFERENCES users(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='报告表'; 
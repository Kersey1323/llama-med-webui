-- 添加用户安全字段的数据库迁移脚本
-- 请在MySQL数据库中执行以下SQL语句

-- 1. 添加安全相关字段到 users 表
ALTER TABLE users 
ADD COLUMN is_verified BOOLEAN DEFAULT FALSE COMMENT '邮箱验证状态',
ADD COLUMN failed_login_attempts INT DEFAULT 0 COMMENT '失败登录次数',
ADD COLUMN locked_until DATETIME NULL COMMENT '锁定截止时间',
ADD COLUMN password_changed_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '密码修改时间',
ADD COLUMN password_history TEXT DEFAULT '[]' COMMENT '密码历史(JSON格式)',
ADD COLUMN two_factor_enabled BOOLEAN DEFAULT FALSE COMMENT '双因素认证启用状态',
ADD COLUMN two_factor_secret VARCHAR(32) NULL COMMENT '双因素认证密钥',
ADD COLUMN current_session_id VARCHAR(64) NULL COMMENT '当前会话ID',
ADD COLUMN last_ip_address VARCHAR(45) NULL COMMENT '最后登录IP地址',
ADD COLUMN last_user_agent TEXT NULL COMMENT '最后登录用户代理',
ADD COLUMN require_password_change BOOLEAN DEFAULT FALSE COMMENT '需要修改密码',
ADD COLUMN account_locked BOOLEAN DEFAULT FALSE COMMENT '账户锁定状态';

-- 2. 创建索引以提高查询性能
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_is_active ON users(is_active);
CREATE INDEX idx_users_account_locked ON users(account_locked);

-- 3. 创建安全事件日志表（可选）
CREATE TABLE IF NOT EXISTS security_events (
    id INT AUTO_INCREMENT PRIMARY KEY,
    event_type VARCHAR(50) NOT NULL COMMENT '事件类型',
    user_id INT NULL COMMENT '用户ID',
    ip_address VARCHAR(45) NULL COMMENT 'IP地址',
    user_agent TEXT NULL COMMENT '用户代理',
    event_details JSON NULL COMMENT '事件详情',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    INDEX idx_security_events_type (event_type),
    INDEX idx_security_events_user (user_id),
    INDEX idx_security_events_ip (ip_address),
    INDEX idx_security_events_created (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='安全事件日志表';

-- 4. 创建登录尝试记录表（可选，用于更精确的速率限制）
CREATE TABLE IF NOT EXISTS login_attempts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(80) NOT NULL COMMENT '用户名',
    ip_address VARCHAR(45) NOT NULL COMMENT 'IP地址',
    success BOOLEAN NOT NULL COMMENT '是否成功',
    user_agent TEXT NULL COMMENT '用户代理',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    INDEX idx_login_attempts_username_ip (username, ip_address),
    INDEX idx_login_attempts_success (success),
    INDEX idx_login_attempts_created (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='登录尝试记录表';

-- 5. 验证表结构
DESCRIBE users;
DESCRIBE security_events;
DESCRIBE login_attempts; 
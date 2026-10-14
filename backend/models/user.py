from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from . import db  # 导入共享的db实例
import json

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    is_active = db.Column(db.Boolean, default=True)
    is_verified = db.Column(db.Boolean, default=False)  # 邮箱验证状态
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # 安全相关字段
    failed_login_attempts = db.Column(db.Integer, default=0)
    locked_until = db.Column(db.DateTime, nullable=True)
    password_changed_at = db.Column(db.DateTime, default=datetime.utcnow)
    password_history = db.Column(db.Text, default='[]')  # JSON格式存储密码历史
    two_factor_enabled = db.Column(db.Boolean, default=False)
    two_factor_secret = db.Column(db.String(32), nullable=True)
    
    # 会话管理
    current_session_id = db.Column(db.String(64), nullable=True)
    last_ip_address = db.Column(db.String(45), nullable=True)  # 支持IPv6
    last_user_agent = db.Column(db.Text, nullable=True)
    
    # 账户安全设置
    require_password_change = db.Column(db.Boolean, default=False)
    account_locked = db.Column(db.Boolean, default=False)
    
    def set_password(self, password):
        """设置密码并更新历史"""
        # 更新密码历史
        history = self.get_password_history()
        history.append(self.password_hash)
        
        # 保持历史记录在指定大小内
        from security.auth_security import SecurityConfig
        if len(history) > SecurityConfig.PASSWORD_HISTORY_SIZE:
            history = history[-SecurityConfig.PASSWORD_HISTORY_SIZE:]
        
        self.password_hash = generate_password_hash(password)
        self.password_history = json.dumps(history)
        self.password_changed_at = datetime.utcnow()
        self.require_password_change = False
        
    def check_password(self, password):
        """检查密码"""
        return check_password_hash(self.password_hash, password)
    
    def is_password_in_history(self, password):
        """检查密码是否在历史记录中"""
        history = self.get_password_history()
        for old_hash in history:
            if check_password_hash(old_hash, password):
                return True
        return False
    
    def get_password_history(self):
        """获取密码历史"""
        try:
            return json.loads(self.password_history) if self.password_history else []
        except (json.JSONDecodeError, TypeError):
            return []
    
    def increment_failed_attempts(self):
        """增加失败登录次数"""
        self.failed_login_attempts += 1
        from security.auth_security import SecurityConfig
        
        if self.failed_login_attempts >= SecurityConfig.ACCOUNT_LOCKOUT_THRESHOLD:
            self.account_locked = True
            self.locked_until = datetime.utcnow() + datetime.timedelta(minutes=SecurityConfig.ACCOUNT_LOCKOUT_DURATION)
    
    def reset_failed_attempts(self):
        """重置失败登录次数"""
        self.failed_login_attempts = 0
        self.locked_until = None
        self.account_locked = False
    
    def is_locked(self):
        """检查账户是否被锁定"""
        if not self.account_locked:
            return False
        
        if self.locked_until and datetime.utcnow() > self.locked_until:
            self.reset_failed_attempts()
            return False
        
        return True
    
    def get_lockout_remaining_time(self):
        """获取剩余锁定时间（秒）"""
        if not self.locked_until:
            return 0
        
        remaining = (self.locked_until - datetime.utcnow()).total_seconds()
        return max(0, int(remaining))
    
    def update_session_info(self, session_id, ip_address, user_agent):
        """更新会话信息"""
        self.current_session_id = session_id
        self.last_ip_address = ip_address
        self.last_user_agent = user_agent
        self.last_login = datetime.utcnow()
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'is_active': self.is_active,
            'is_verified': self.is_verified,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'last_login': self.last_login.strftime('%Y-%m-%d %H:%M:%S') if self.last_login else None,
            'two_factor_enabled': self.two_factor_enabled,
            'require_password_change': self.require_password_change,
            'account_locked': self.account_locked
        }
    
    def __repr__(self):
        return f'<User {self.username}>' 
import re
import hashlib
import secrets
import time
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify, session, current_app
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import jwt
from werkzeug.security import generate_password_hash, check_password_hash
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SecurityConfig:
    """安全配置类"""
    
    # 密码策略
    MIN_PASSWORD_LENGTH = 12
    REQUIRE_UPPERCASE = True
    REQUIRE_LOWERCASE = True
    REQUIRE_DIGITS = True
    REQUIRE_SPECIAL_CHARS = True
    SPECIAL_CHARS = "!@#$%^&*()_+-=[]{}|;:,.<>?"
    
    # 登录安全
    MAX_LOGIN_ATTEMPTS = 5
    LOCKOUT_DURATION = 15  # 分钟
    SESSION_TIMEOUT = 30  # 分钟
    
    # JWT配置
    JWT_SECRET_KEY = None  # 将在初始化时设置
    JWT_ALGORITHM = 'HS256'
    JWT_EXPIRATION = 3600  # 1小时
    
    # 密码历史
    PASSWORD_HISTORY_SIZE = 5
    
    # 账户锁定
    ACCOUNT_LOCKOUT_THRESHOLD = 10
    ACCOUNT_LOCKOUT_DURATION = 60  # 分钟

class PasswordValidator:
    """密码验证器"""
    
    @staticmethod
    def validate_password(password):
        """验证密码强度"""
        errors = []
        
        if len(password) < SecurityConfig.MIN_PASSWORD_LENGTH:
            errors.append(f"密码长度至少需要{SecurityConfig.MIN_PASSWORD_LENGTH}个字符")
        
        if SecurityConfig.REQUIRE_UPPERCASE and not re.search(r'[A-Z]', password):
            errors.append("密码必须包含至少一个大写字母")
        
        if SecurityConfig.REQUIRE_LOWERCASE and not re.search(r'[a-z]', password):
            errors.append("密码必须包含至少一个小写字母")
        
        if SecurityConfig.REQUIRE_DIGITS and not re.search(r'\d', password):
            errors.append("密码必须包含至少一个数字")
        
        if SecurityConfig.REQUIRE_SPECIAL_CHARS and not any(c in SecurityConfig.SPECIAL_CHARS for c in password):
            errors.append("密码必须包含至少一个特殊字符")
        
        # 检查常见弱密码
        weak_passwords = ['password', '123456', 'qwerty', 'admin', 'letmein']
        if password.lower() in weak_passwords:
            errors.append("密码过于简单，请选择更复杂的密码")
        
        return errors
    
    @staticmethod
    def generate_strong_password(length=16):
        """生成强密码"""
        import string
        chars = string.ascii_letters + string.digits + SecurityConfig.SPECIAL_CHARS
        while True:
            password = ''.join(secrets.choice(chars) for _ in range(length))
            if not PasswordValidator.validate_password(password):
                return password

class RateLimiter:
    """速率限制器"""
    
    def __init__(self, app):
        self.limiter = Limiter(
            app,
            key_func=get_remote_address,
            default_limits=["200 per day", "50 per hour"]
        )
    
    def login_limit(self):
        """登录速率限制装饰器"""
        return self.limiter.limit("5 per minute")
    
    def register_limit(self):
        """注册速率限制装饰器"""
        return self.limiter.limit("3 per hour")
    
    def api_limit(self):
        """API速率限制装饰器"""
        return self.limiter.limit("1000 per hour")

class SessionManager:
    """会话管理器"""
    
    @staticmethod
    def create_session(user_id, ip_address, user_agent):
        """创建安全会话"""
        session_id = secrets.token_urlsafe(32)
        session_data = {
            'user_id': user_id,
            'ip_address': ip_address,
            'user_agent': user_agent,
            'created_at': datetime.utcnow(),
            'last_activity': datetime.utcnow(),
            'session_id': session_id
        }
        
        # 在实际应用中，这里应该将会话数据存储到Redis或数据库
        return session_id, session_data
    
    @staticmethod
    def validate_session(session_data, ip_address, user_agent):
        """验证会话有效性"""
        if not session_data:
            return False
        
        # 检查会话是否过期
        if datetime.utcnow() - session_data['last_activity'] > timedelta(minutes=SecurityConfig.SESSION_TIMEOUT):
            return False
        
        # 检查IP地址是否匹配（可选，取决于安全要求）
        if session_data.get('ip_address') != ip_address:
            logger.warning(f"IP地址不匹配: {session_data.get('ip_address')} vs {ip_address}")
            return False
        
        # 更新最后活动时间
        session_data['last_activity'] = datetime.utcnow()
        return True

class LoginAttemptTracker:
    """登录尝试跟踪器"""
    
    def __init__(self):
        self.attempts = {}  # 在实际应用中应该使用Redis
    
    def record_attempt(self, username, ip_address, success):
        """记录登录尝试"""
        key = f"{username}:{ip_address}"
        if key not in self.attempts:
            self.attempts[key] = []
        
        self.attempts[key].append({
            'timestamp': datetime.utcnow(),
            'success': success,
            'ip_address': ip_address
        })
        
        # 清理旧的尝试记录
        cutoff_time = datetime.utcnow() - timedelta(minutes=SecurityConfig.LOCKOUT_DURATION)
        self.attempts[key] = [a for a in self.attempts[key] if a['timestamp'] > cutoff_time]
    
    def is_locked_out(self, username, ip_address):
        """检查是否被锁定"""
        key = f"{username}:{ip_address}"
        if key not in self.attempts:
            return False
        
        recent_attempts = [a for a in self.attempts[key] 
                          if not a['success'] and 
                          a['timestamp'] > datetime.utcnow() - timedelta(minutes=SecurityConfig.LOCKOUT_DURATION)]
        
        return len(recent_attempts) >= SecurityConfig.MAX_LOGIN_ATTEMPTS
    
    def get_remaining_lockout_time(self, username, ip_address):
        """获取剩余锁定时间"""
        key = f"{username}:{ip_address}"
        if key not in self.attempts:
            return 0
        
        failed_attempts = [a for a in self.attempts[key] if not a['success']]
        if not failed_attempts:
            return 0
        
        oldest_failed = min(failed_attempts, key=lambda x: x['timestamp'])
        lockout_end = oldest_failed['timestamp'] + timedelta(minutes=SecurityConfig.LOCKOUT_DURATION)
        remaining = (lockout_end - datetime.utcnow()).total_seconds()
        
        return max(0, int(remaining))

class SecurityMiddleware:
    """安全中间件"""
    
    @staticmethod
    def security_headers(response):
        """添加安全响应头"""
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'"
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        return response
    
    @staticmethod
    def validate_request():
        """验证请求安全性"""
        # 检查请求头
        if 'X-Requested-With' not in request.headers:
            return False, "缺少X-Requested-With头"
        
        # 检查Content-Type
        if request.method == 'POST' and 'application/json' not in request.content_type:
            return False, "Content-Type必须是application/json"
        
        return True, None

class JWTManager:
    """JWT管理器"""
    
    @staticmethod
    def create_token(user_id, additional_claims=None):
        """创建JWT令牌"""
        payload = {
            'user_id': user_id,
            'exp': datetime.utcnow() + timedelta(seconds=SecurityConfig.JWT_EXPIRATION),
            'iat': datetime.utcnow(),
            'jti': secrets.token_urlsafe(16)  # JWT ID
        }
        
        if additional_claims:
            payload.update(additional_claims)
        
        return jwt.encode(payload, SecurityConfig.JWT_SECRET_KEY, algorithm=SecurityConfig.JWT_ALGORITHM)
    
    @staticmethod
    def verify_token(token):
        """验证JWT令牌"""
        try:
            payload = jwt.decode(token, SecurityConfig.JWT_SECRET_KEY, algorithms=[SecurityConfig.JWT_ALGORITHM])
            return True, payload
        except jwt.ExpiredSignatureError:
            return False, "令牌已过期"
        except jwt.InvalidTokenError:
            return False, "无效令牌"
        except Exception as e:
            return False, f"令牌验证失败: {str(e)}"

# 全局实例
login_tracker = LoginAttemptTracker()

def require_security_headers(f):
    """要求安全头的装饰器"""
    @wraps(f)
    def decorated(*args, **kwargs):
        is_valid, error_msg = SecurityMiddleware.validate_request()
        if not is_valid:
            return jsonify({'error': error_msg}), 400
        return f(*args, **kwargs)
    return decorated

def log_security_event(event_type, user_id=None, ip_address=None, details=None):
    """记录安全事件"""
    logger.info(f"SECURITY_EVENT: {event_type} | User: {user_id} | IP: {ip_address} | Details: {details}") 
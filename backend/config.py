import os
from datetime import timedelta


# 通用API配置
API_KEY = os.environ.get("API_KEY", "sk-56819adebf7c40b4a52d6f3191667910")
BASE_URL = os.environ.get("BASE_URL", "https://api.deepseek.com/v1")
MODEL_NAME = os.environ.get("MODEL_NAME", "deepseek-chat")
LOCAL_API_KEY = os.environ.get("LOCAL_API_KEY", "0")
LOCAL_BASE_URL = os.environ.get("LOCAL_BASE_URL", "http://host.docker.internal:5000/v1")
LOCAL_MODEL_NAME = os.environ.get("LOCAL_MODEL_NAME", "test")
# Redis配置
REDIS_HOST = os.environ.get('REDIS_HOST') or 'localhost'  # 本地运行时使用localhost
REDIS_PORT = int(os.environ.get('REDIS_PORT') or 6379)
REDIS_DB = int(os.environ.get('REDIS_DB') or 0)
REDIS_PASSWORD = os.environ.get('REDIS_PASSWORD') or ""

class Config:
    """基础配置类"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production-123456789'
    
    # docker数据库配置
    MYSQL_HOST = os.environ.get('MYSQL_HOST') or 'mysql'
    MYSQL_PORT = int(os.environ.get('MYSQL_PORT') or 3306)
    MYSQL_USER = os.environ.get('MYSQL_USER') or 'user'
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD') or 'password'
    MYSQL_DATABASE = os.environ.get('MYSQL_DATABASE') or 'llama_med_db'

    # SQLAlchemy配置
    SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}?charset=utf8mb4'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 10,
        'pool_recycle': 3600,
        'pool_pre_ping': True
    }
    
    # JWT配置
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'dev-jwt-secret-key-change-in-production-987654321'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    JWT_ERROR_MESSAGE_KEY = 'error'
    
    # 会话配置
    SESSION_TYPE = 'filesystem'
    SESSION_FILE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sessions')
    SESSION_FILE_THRESHOLD = 500
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=30)
    
    # 安全配置
    SECURITY_PASSWORD_SALT = os.environ.get('SECURITY_PASSWORD_SALT') or 'dev-password-salt-change-in-production-456789123'
    
    # 文件上传配置
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
    OUTPUT_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'outputs')
    

    
    # 本地API配置
    LOCAL_API_KEY = os.environ.get('LOCAL_API_KEY') or '0'
    LOCAL_BASE_URL = os.environ.get('LOCAL_BASE_URL') or 'http://host.docker.internal:5000/v1'
    LOCAL_MODEL_NAME = os.environ.get('LOCAL_MODEL_NAME') or 'test'
    
    # 安全配置
    SECURITY_CONFIG = {
        # 密码策略
        'MIN_PASSWORD_LENGTH': 12,
        'REQUIRE_UPPERCASE': True,
        'REQUIRE_LOWERCASE': True,
        'REQUIRE_DIGITS': True,
        'REQUIRE_SPECIAL_CHARS': True,
        'SPECIAL_CHARS': "!@#$%^&*()_+-=[]{}|;:,.<>?",
        'PASSWORD_HISTORY_SIZE': 5,
        
        # 登录安全
        'MAX_LOGIN_ATTEMPTS': 5,
        'LOCKOUT_DURATION': 15,  # 分钟
        'SESSION_TIMEOUT': 30,  # 分钟
        'ACCOUNT_LOCKOUT_THRESHOLD': 10,
        'ACCOUNT_LOCKOUT_DURATION': 60,  # 分钟
        
        # JWT配置
        'JWT_EXPIRATION': 3600,  # 1小时
        'JWT_ALGORITHM': 'HS256',
        
        # 速率限制
        'RATE_LIMIT_LOGIN': '5 per minute',
        'RATE_LIMIT_REGISTER': '3 per hour',
        'RATE_LIMIT_API': '1000 per hour',
        
        # 安全头
        'ENABLE_SECURITY_HEADERS': True,
        'ENABLE_HTTPS_ONLY': True,
        'ENABLE_CSP': True,
        
        # 日志配置
        'LOG_SECURITY_EVENTS': True,
        'LOG_LEVEL': 'INFO'
    }
    
    # 跨域配置
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', 'http://localhost:3000,http://localhost:8080').split(',')
    CORS_SUPPORTS_CREDENTIALS = True
    
    # 日志配置
    LOG_LEVEL = os.environ.get('LOG_LEVEL') or 'INFO'
    LOG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs', 'app.log')
    
    # 缓存配置
    CACHE_TYPE = 'simple'
    CACHE_DEFAULT_TIMEOUT = 300
    
    # 邮件配置（用于邮箱验证）
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'smtp.gmail.com'
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() == 'true'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER')

class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True
    TESTING = False
    
    # 开发环境安全配置（相对宽松）
    SECURITY_CONFIG = {
        **Config.SECURITY_CONFIG,
        'MIN_PASSWORD_LENGTH': 8,
        'MAX_LOGIN_ATTEMPTS': 10,
        'LOCKOUT_DURATION': 5,
        'ENABLE_HTTPS_ONLY': False,
        'LOG_LEVEL': 'DEBUG'
    }
    # 本地数据库配置
    MYSQL_HOST = os.environ.get('MYSQL_HOST') or 'localhost'
    MYSQL_PORT = int(os.environ.get('MYSQL_PORT') or 3306)
    MYSQL_USER = os.environ.get('MYSQL_USER') or 'root'
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD') or '12345'
    MYSQL_DATABASE = os.environ.get('MYSQL_DATABASE') or 'llama_med_db'
    # SQLAlchemy配置
    SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}?charset=utf8mb4'
    # 开发环境安全配置（相对宽松）
    SECURITY_CONFIG = {
        **Config.SECURITY_CONFIG,
        'MIN_PASSWORD_LENGTH': 8,
        'MAX_LOGIN_ATTEMPTS': 10,
        'LOCKOUT_DURATION': 5,
        'ENABLE_HTTPS_ONLY': False,
        'LOG_LEVEL': 'DEBUG'
    }

class ProductionConfig(Config):
    DEBUG = False
    TESTING = False
    MYSQL_HOST = os.environ.get('MYSQL_HOST') or 'mysql'
    MYSQL_PORT = int(os.environ.get('MYSQL_PORT') or 33306)
    MYSQL_USER = os.environ.get('MYSQL_USER') or 'user'
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD') or 'password'
    MYSQL_DATABASE = os.environ.get('MYSQL_DATABASE') or 'llama_med_db'

    # 生产环境检查（可选）
    def __init__(self):
        super().__init__()
        # 只有在明确设置为生产环境时才检查
        if os.environ.get('FLASK_ENV') == 'production':
            if not all([self.SECRET_KEY != 'dev-secret-key-change-in-production-123456789',
                       self.JWT_SECRET_KEY != 'dev-jwt-secret-key-change-in-production-987654321',
                       self.SECURITY_PASSWORD_SALT != 'dev-password-salt-change-in-production-456789123']):
                raise ValueError("生产环境必须设置 SECRET_KEY, JWT_SECRET_KEY, 和 SECURITY_PASSWORD_SALT 环境变量")
    
    # 生产环境安全配置（严格）
    SECURITY_CONFIG = {
        **Config.SECURITY_CONFIG,
        'MIN_PASSWORD_LENGTH': 12,
        'MAX_LOGIN_ATTEMPTS': 5,
        'LOCKOUT_DURATION': 15,
        'ENABLE_HTTPS_ONLY': True,
        'LOG_LEVEL': 'WARNING'
    }

class TestingConfig(Config):
    """测试环境配置"""
    DEBUG = True
    TESTING = True
    
    # 测试环境使用内存数据库
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    
    # 测试环境安全配置（最宽松）
    SECURITY_CONFIG = {
        **Config.SECURITY_CONFIG,
        'MIN_PASSWORD_LENGTH': 6,
        'MAX_LOGIN_ATTEMPTS': 100,
        'LOCKOUT_DURATION': 1,
        'ENABLE_HTTPS_ONLY': False,
        'LOG_LEVEL': 'DEBUG'
    }

# 配置映射
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
} 


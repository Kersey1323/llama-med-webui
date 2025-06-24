from flask_sqlalchemy import SQLAlchemy

# 创建数据库实例
db = SQLAlchemy()

# 注意：为避免循环导入，不要在此导入模型
# 这些导入将在app.py中显式处理 
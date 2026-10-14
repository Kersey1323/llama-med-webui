from flask import Flask
from routes.batch_process import batch_bp
from routes.annotation import annotation_bp
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from models import db
from models.role import Role
from config import config

# 导入auth蓝图
from auth.routes import auth_bp
import os


env = os.environ.get("FLASK_ENV", "development")


def create_app():
    app = Flask(__name__)
    app.config.from_object(config[env])

    # 初始化扩展
    CORS(
        app,
        resources={
            r"/*": {
                "origins": [
                    "http://localhost:8000",
                    "http://localhost:5173",
                    "http://127.0.0.1:5173",
                    "http://0.0.0.0:8000",
                    "http://0.0.0.0:5173",
                    "http://localhost:8003",
                    "http://0.0.0.0:8003",
                    "http://localhost",  # 添加localhost支持
                    "*",
                ],
                "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
                "allow_headers": [
                    "Content-Type",
                    "Authorization",
                    "Referer,Accept,Origin,User-Agent",
                ],
                "supports_credentials": True,
            }
        },
    )
    db.init_app(app)
    jwt = JWTManager(app)

    # 初始化安全配置
    from security.auth_security import SecurityConfig

    SecurityConfig.JWT_SECRET_KEY = app.config["JWT_SECRET_KEY"]

    # 注册蓝图
    # app.register_blueprint(medLLM_routes)
    # app.register_blueprint(corrector_routes)
    app.register_blueprint(batch_bp, url_prefix="/api/batch")
    app.register_blueprint(annotation_bp)
    app.register_blueprint(auth_bp, url_prefix="/api/auth")

    # 创建数据库表
    with app.app_context():
        # 显式检查并且删除表（仅在开发环境中使用）
        # db.drop_all()  # 谨慎使用，会删除所有数据
        db.create_all()

        # 创建角色（如果不存在）
        if not Role.query.filter_by(name="admin").first():
            admin_role = Role(name="admin", description="Administrator")
            db.session.add(admin_role)
            db.session.commit()

        if not Role.query.filter_by(name="user").first():
            user_role = Role(name="user", description="Regular user")
            db.session.add(user_role)
            db.session.commit()

    return app


if __name__ == "__main__":

    app = create_app()
    # 使用环境变量中的端口，默认为5000
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port, debug=True)

from functools import wraps
from flask import jsonify, g, request
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from models.user import User


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        # 临时跳过验证
        dummy_user = User.query.first()
        g.user_id = dummy_user.id if dummy_user else 1  # 假设存在ID=1的测试用户
        return f(*args, **kwargs)
    return decorated

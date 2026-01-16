from functools import wraps
from flask import jsonify, request
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from models.user import User
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        # 直接跳过验证逻辑
        dummy_user = User.query.first()  # 获取第一个用户作为测试用户
        return f(dummy_user, *args, **kwargs)
    return decorated

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        # 直接跳过验证逻辑
        dummy_user = User.query.first()
        return f(dummy_user, *args, **kwargs)
    return decorated

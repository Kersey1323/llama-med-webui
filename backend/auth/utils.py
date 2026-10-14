from functools import wraps
from flask import jsonify, request
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from models.user import User
# def token_required(f):
#     @wraps(f)
#     def decorated(*args, **kwargs):
#         try:
#             verify_jwt_in_request()
#             current_user = User.query.get(get_jwt_identity())
#             if not current_user:
#                 return jsonify({'message': 'User not found'}), 404
#             return f(current_user, *args, **kwargs)
#         except Exception as e:
#             return jsonify({'message': str(e)}), 401
#     return decorated
#
# def admin_required(f):
#     @wraps(f)
#     def decorated(*args, **kwargs):
#         try:
#             verify_jwt_in_request()
#             current_user = User.query.get(get_jwt_identity())
#             if not current_user:
#                 return jsonify({'message': 'User not found'}), 404
#             if not any(role.name == 'admin' for role in current_user.roles):
#                 return jsonify({'message': 'Admin access required'}), 403
#             return f(current_user, *args, **kwargs)
#         except Exception as e:
#             return jsonify({'message': str(e)}), 401
#     return decorated
# utils.py

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

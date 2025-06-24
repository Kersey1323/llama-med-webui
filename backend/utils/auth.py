from functools import wraps
from flask import jsonify, g, request
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from backend.models.user import User

# def login_required(f):
#     @wraps(f)
#     def decorated(*args, **kwargs):
#         try:
#             verify_jwt_in_request()
#             current_user_id = get_jwt_identity()
#             # 存储用户ID到g对象中，以便在视图函数中使用
#             g.user_id = current_user_id
#             print(f"Current user ID: {get_jwt_identity()}")  # 打印用户标识
#             # 检查用户是否存在
#             current_user = User.query.get(current_user_id)
#             if not current_user:
#                 return jsonify({'error': '用户不存在'}), 404
#
#             return f(*args, **kwargs)
#         except Exception as e:
#             return jsonify({'error': '请先登录', 'details': str(e)}), 401
#     return decorated

# auth.py
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        # 临时跳过验证
        dummy_user = User.query.first()
        g.user_id = dummy_user.id if dummy_user else 1  # 假设存在ID=1的测试用户
        return f(*args, **kwargs)
    return decorated

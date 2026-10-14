"""Authentication gate with an explicit, reversible local preview switch."""
import os
from functools import wraps
from flask import current_app, jsonify, g, session
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from flask_jwt_extended.exceptions import JWTExtendedException
from jwt.exceptions import PyJWTError
from models.user import User


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        disabled = current_app.config.get(
            'AUTH_DISABLED', os.environ.get('AUTH_DISABLED', 'true').lower() == 'true'
        )
        if disabled:
            # Use a chosen existing account, never an arbitrary first user or a fake ID.
            user_id = current_app.config.get('DEMO_USER_ID', os.environ.get('DEMO_USER_ID', '1'))
            user = User.query.get(user_id)
            if not user or not user.is_active:
                return jsonify({'error': '免登录账户不可用，请配置 DEMO_USER_ID 为有效的现有用户 ID'}), 503
        else:
            try:
                verify_jwt_in_request()
                user = User.query.get(get_jwt_identity())
            except (JWTExtendedException, PyJWTError):
                return jsonify({'error': '请先登录'}), 401
            if not user or not user.is_active:
                return jsonify({'error': '账户不可用'}), 401
        # Existing batch and annotation APIs read session; newer APIs read g.
        g.user_id = user.id
        session['user_id'] = user.id
        return f(*args, **kwargs)
    return decorated

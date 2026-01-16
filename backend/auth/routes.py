from flask import Blueprint, request, jsonify, session
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from models.user import User, db
from models.role import Role
from models.user_role import UserRole
from security.auth_security import (
    PasswordValidator, login_tracker, SecurityConfig, 
    JWTManager, SessionManager, log_security_event,
    require_security_headers
)
from datetime import datetime
import secrets
import re
import io
import base64
import uuid
from PIL import Image, ImageDraw, ImageFont, ImageFilter

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/health', methods=['GET'])
def health_check():
    """健康检查端点"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'auth'
    }), 200

@auth_bp.route('/register', methods=['POST'])
@require_security_headers
def register():
    """用户注册"""
    data = request.get_json()
    
    # 验证码校验
    captcha = data.get('captcha', '').lower()
    captcha_uuid = data.get('captcha_uuid')
    session_captcha = session.get('captcha', {}).get(captcha_uuid, '').lower() if session.get('captcha') else ''
    if not captcha or not captcha_uuid or captcha != session_captcha:
        return jsonify({'error': '验证码错误'}), 400
    # 校验通过后删除该 uuid，防止重用
    if session.get('captcha') and captcha_uuid in session['captcha']:
        del session['captcha'][captcha_uuid]
        session.modified = True
    
    # 验证必需字段
    required_fields = ['username', 'email', 'password']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'error': f'缺少必需字段: {field}'}), 400
    
    # 验证用户名格式
    if not re.match(r'^[a-zA-Z0-9_]{3,20}$', data['username']):
        return jsonify({'error': '用户名只能包含字母、数字和下划线，长度3-20位'}), 400
    
    # 验证邮箱格式
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, data['email']):
        return jsonify({'error': '邮箱格式不正确'}), 400
    
    # 验证密码强度
    password_errors = PasswordValidator.validate_password(data['password'])
    if password_errors:
        return jsonify({'error': '密码不符合要求', 'details': password_errors}), 400
    
    # 检查用户名和邮箱是否已存在
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': '用户名已存在'}), 400
        
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': '邮箱已存在'}), 400
    
    try:
        # 创建用户
        user = User(
            username=data['username'],
            email=data['email']
        )
        user.set_password(data['password'])
        
        # 默认角色
        default_role = Role.query.filter_by(name='user').first()
        if not default_role:
            default_role = Role(name='user', description='Regular user')
            db.session.add(default_role)
        
        db.session.add(user)
        db.session.commit()
        
        # 分配默认角色
        user_role = UserRole(user_id=user.id, role_id=default_role.id)
        db.session.add(user_role)
        db.session.commit()
        
        # 记录安全事件
        log_security_event('USER_REGISTERED', user.id, request.remote_addr, 
                          {'username': user.username, 'email': user.email})
        
        return jsonify({'message': '用户注册成功，请登录'}), 201
        
    except Exception as e:
        db.session.rollback()
        log_security_event('REGISTRATION_FAILED', None, request.remote_addr, 
                          {'error': str(e), 'username': data.get('username')})
        return jsonify({'error': '注册失败，请稍后重试'}), 500

@auth_bp.route('/login', methods=['POST'])
@require_security_headers
def login():
    """用户登录"""
    data = request.get_json()
    
    # 验证码校验
    captcha = data.get('captcha', '').lower()
    captcha_uuid = data.get('captcha_uuid')
    session_captcha = session.get('captcha', {}).get(captcha_uuid, '').lower() if session.get('captcha') else ''
    if not captcha or not captcha_uuid or captcha != session_captcha:
        return jsonify({'error': '验证码错误'}), 400
    # 校验通过后删除该 uuid，防止重用
    if session.get('captcha') and captcha_uuid in session['captcha']:
        del session['captcha'][captcha_uuid]
        session.modified = True
    
    if not data.get('username') or not data.get('password'):
        return jsonify({'error': '用户名/邮箱和密码不能为空'}), 400
    
    username_or_email = data['username']
    password = data['password']
    ip_address = request.remote_addr
    user_agent = request.headers.get('User-Agent', '')
    
    # 检查是否被锁定
    if login_tracker.is_locked_out(username_or_email, ip_address):
        remaining_time = login_tracker.get_remaining_lockout_time(username_or_email, ip_address)
        return jsonify({
            'error': f'账户已被锁定，请{remaining_time}秒后重试'
        }), 429
    
    try:
        # 支持用户名或邮箱登录
        user = User.query.filter((User.username == username_or_email) | (User.email == username_or_email)).first()
        
        # 验证用户和密码
        if not user or not user.check_password(password):
            login_tracker.record_attempt(username_or_email, ip_address, False)
            log_security_event('LOGIN_FAILED', user.id if user else None, ip_address, 
                              {'username_or_email': username_or_email, 'reason': 'invalid_credentials'})
            return jsonify({'error': '用户名/邮箱或密码错误'}), 401
        
        # 检查账户状态
        if not user.is_active:
            log_security_event('LOGIN_FAILED', user.id, ip_address, 
                              {'username_or_email': username_or_email, 'reason': 'account_inactive'})
            return jsonify({'error': '账户已被禁用'}), 403
        
        if user.is_locked():
            remaining_time = user.get_lockout_remaining_time()
            return jsonify({
                'error': f'账户已被锁定，请{remaining_time}秒后重试'
            }), 429
        
        # 登录成功
        login_tracker.record_attempt(username_or_email, ip_address, True)
        user.reset_failed_attempts()
        
        # 创建会话
        session_id, session_data = SessionManager.create_session(
            user.id, ip_address, user_agent
        )
        
        # 更新用户会话信息
        user.update_session_info(session_id, ip_address, user_agent)
        
        # 创建JWT令牌
        token = JWTManager.create_token(user.id, {
            'username': user.username,
            'session_id': session_id
        })
        
        # 设置会话
        session['user_id'] = user.id
        session['session_id'] = session_id
        
        db.session.commit()
        
        # 记录安全事件
        log_security_event('LOGIN_SUCCESS', user.id, ip_address, 
                          {'username_or_email': username_or_email, 'session_id': session_id})
        
        return jsonify({
            'access_token': token,
            'user': user.to_dict(),
            'session_id': session_id
        }), 200
        
    except Exception as e:
        db.session.rollback()
        log_security_event('LOGIN_ERROR', None, ip_address, 
                          {'error': str(e), 'username_or_email': username_or_email})
        return jsonify({'error': '登录失败，请稍后重试'}), 500

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """用户登出"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if user:
            # 清除会话信息
            user.current_session_id = None
            db.session.commit()
            
            # 记录安全事件
            log_security_event('LOGOUT', user.id, request.remote_addr, 
                              {'username': user.username})
        
        # 清除会话
        session.clear()
        
        return jsonify({'message': '登出成功'}), 200
        
    except Exception as e:
        log_security_event('LOGOUT_ERROR', None, request.remote_addr, 
                          {'error': str(e)})
        return jsonify({'error': '登出失败'}), 500

@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def profile():
    """获取用户信息"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': '用户不存在'}), 404
        
        # 检查是否需要强制修改密码
        if user.require_password_change:
            return jsonify({
                'error': '需要修改密码',
                'require_password_change': True
            }), 403
        
        return jsonify({
            'user': user.to_dict(),
            'roles': [role.name for role in user.roles]
        }), 200
        
    except Exception as e:
        return jsonify({'error': '获取用户信息失败'}), 500

@auth_bp.route('/change-password', methods=['POST'])
@jwt_required()
@require_security_headers
def change_password():
    """修改密码"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': '用户不存在'}), 404
        
        data = request.get_json()
        current_password = data.get('current_password')
        new_password = data.get('new_password')
        
        if not current_password or not new_password:
            return jsonify({'error': '当前密码和新密码不能为空'}), 400
        
        # 验证当前密码
        if not user.check_password(current_password):
            return jsonify({'error': '当前密码错误'}), 400
        
        # 验证新密码强度
        password_errors = PasswordValidator.validate_password(new_password)
        if password_errors:
            return jsonify({'error': '新密码不符合要求', 'details': password_errors}), 400
        
        # 检查新密码是否在历史记录中
        if user.is_password_in_history(new_password):
            return jsonify({'error': '新密码不能与最近使用过的密码相同'}), 400
        
        # 更新密码
        user.set_password(new_password)
        db.session.commit()
        
        # 记录安全事件
        log_security_event('PASSWORD_CHANGED', user.id, request.remote_addr, 
                          {'username': user.username})
        
        return jsonify({'message': '密码修改成功'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': '密码修改失败'}), 500

@auth_bp.route('/security-status', methods=['GET'])
@jwt_required()
def security_status():
    """获取账户安全状态"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': '用户不存在'}), 404
        
        return jsonify({
            'failed_login_attempts': user.failed_login_attempts,
            'account_locked': user.account_locked,
            'lockout_remaining_time': user.get_lockout_remaining_time(),
            'two_factor_enabled': user.two_factor_enabled,
            'require_password_change': user.require_password_change,
            'last_login': user.last_login.strftime('%Y-%m-%d %H:%M:%S') if user.last_login else None,
            'last_ip_address': user.last_ip_address
        }), 200
        
    except Exception as e:
        return jsonify({'error': '获取安全状态失败'}), 500

@auth_bp.route('/captcha', methods=['GET'])
def get_captcha():
    # 生成随机验证码文本
    chars = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789'
    captcha_text = ''.join(secrets.choice(chars) for _ in range(5))
    captcha_uuid = str(uuid.uuid4())

    # 生成图片
    width, height = 120, 40
    image = Image.new('RGB', (width, height), (255, 255, 255))
    font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf', 28)  # 确保有arial.ttf字体文件
    draw = ImageDraw.Draw(image)

    # 随机画干扰线
    for _ in range(5):
        x1 = secrets.randbelow(width)
        y1 = secrets.randbelow(height)
        x2 = secrets.randbelow(width)
        y2 = secrets.randbelow(height)
        draw.line(((x1, y1), (x2, y2)), fill=(secrets.randbelow(256), secrets.randbelow(256), secrets.randbelow(256)), width=2)

    # 画验证码字符
    for i, char in enumerate(captcha_text):
        x = 10 + i * 22
        y = secrets.randbelow(8)
        draw.text((x, y), char, font=font, fill=(secrets.randbelow(100), secrets.randbelow(100), secrets.randbelow(100)))

    # 模糊处理
    image = image.filter(ImageFilter.BLUR)

    # 转为base64
    buf = io.BytesIO()
    image.save(buf, format='PNG')
    img_base64 = 'data:image/png;base64,' + base64.b64encode(buf.getvalue()).decode()

    # 存入session
    if 'captcha' not in session:
        session['captcha'] = {}
    session['captcha'][captcha_uuid] = captcha_text.lower()
    session.modified = True

    return jsonify({'img': img_base64, 'uuid': captcha_uuid}) 
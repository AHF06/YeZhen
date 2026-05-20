from flask import request
from app.utils.response import success, error
from app.models.base import db
from app.models.user import User
import hashlib
import re


def register_auth_routes(app):
    
    # ========== 微信登录 ==========
    @app.route('/api/auth/wechat-login', methods=['POST'])
    def wechat_login():
        """微信一键登录"""
        data = request.get_json()
        code = data.get('code')
        
        if not code:
            return error('获取微信授权失败', 400)
        
        # TODO: 调用微信接口获取 openid
        mock_openid = f"wx_openid_{hashlib.md5(code.encode()).hexdigest()[:16]}"
        
        user = User.query.filter_by(openid=mock_openid).first()
        
        if not user:
            username = User.generate_username()
            user = User(
                phone='',
                password='',
                username=username,
                nickname=username,
                openid=mock_openid
            )
            db.session.add(user)
            db.session.commit()
        
        token = hashlib.md5(f"{user.id}{user.username}".encode()).hexdigest()
        
        return success({
            'user_id': user.id,
            'username': user.username,
            'nickname': user.nickname,
            'avatar': user.avatar,
            'phone': user.phone,
            'token': token
        }, '登录成功')
    
    # ========== 手机号注册 ==========
    @app.route('/api/auth/register', methods=['POST'])
    def register():
        """手机号注册"""
        data = request.get_json()
        
        phone = data.get('phone', '').strip()
        password = data.get('password', '').strip()
        nickname = data.get('nickname', '').strip()
        
        if not phone:
            return error('请输入手机号', 400)
        if not re.match(r'^1[3-9]\d{9}$', phone):
            return error('请输入正确的手机号', 400)
        if not password:
            return error('请输入密码', 400)
        if len(password) < 6:
            return error('密码长度不能小于6位', 400)
        
        existing = User.query.filter_by(phone=phone).first()
        if existing:
            return error('该手机号已注册', 400)
        
        username = User.generate_username()
        while User.query.filter_by(username=username).first():
            username = User.generate_username()
        
        hashed_password = hashlib.md5(password.encode()).hexdigest()
        
        user = User(
            phone=phone,
            password=hashed_password,
            username=username,
            nickname=nickname if nickname else username
        )
        db.session.add(user)
        db.session.commit()
        
        token = hashlib.md5(f"{user.id}{user.username}".encode()).hexdigest()
        
        return success({
            'user_id': user.id,
            'username': user.username,
            'nickname': user.nickname,
            'avatar': user.avatar,
            'phone': user.phone,
            'token': token
        }, '注册成功')
    
    # ========== 手机号密码登录 ==========
    @app.route('/api/auth/login', methods=['POST'])
    def login():
        """手机号密码登录"""
        data = request.get_json()

        phone = data.get('phone', '').strip()
        password = data.get('password', '').strip()

        if not phone or not password:
            return error('请输入手机号和密码', 400)
        
        hashed_password = hashlib.md5(password.encode()).hexdigest()
        user = User.query.filter_by(phone=phone, password=hashed_password).first()
        
        if not user:
            return error('手机号或密码错误', 401)
        
        token = hashlib.md5(f"{user.id}{user.username}".encode()).hexdigest()
        
        return success({
            'user_id': user.id,
            'username': user.username,
            'nickname': user.nickname,
            'avatar': user.avatar,
            'phone': user.phone,
            'token': token
        }, '登录成功')
    
    # ========== 获取用户信息 ==========
    @app.route('/api/auth/user-info', methods=['GET'])
    def get_user_info():
        """获取用户信息"""
        user_id = request.args.get('user_id', type=int)
        
        if not user_id:
            return error('缺少用户ID', 400)
        
        user = User.query.get(user_id)
        if not user:
            return error('用户不存在', 404)
        
        return success(user.to_dict())
    
    # ========== 修改昵称 ==========
    @app.route('/api/auth/update-nickname', methods=['POST'])
    def update_nickname():
        """修改昵称"""
        data = request.get_json()
        
        user_id = data.get('user_id')
        nickname = data.get('nickname', '').strip()
        
        if not user_id:
            return error('缺少用户ID', 400)
        if not nickname:
            return error('昵称不能为空', 400)
        
        user = User.query.get(user_id)
        if not user:
            return error('用户不存在', 404)
        
        user.nickname = nickname
        db.session.commit()
        
        return success({'nickname': user.nickname}, '昵称修改成功')
    
    # ========== 修改用户名 ==========
    @app.route('/api/auth/update-username', methods=['POST'])
    def update_username():
        """修改用户名"""
        data = request.get_json()
        
        user_id = data.get('user_id')
        username = data.get('username', '').strip()
        
        if not user_id:
            return error('缺少用户ID', 400)
        if not username:
            return error('用户名不能为空', 400)
        if len(username) < 2 or len(username) > 20:
            return error('用户名长度应为2-20个字符', 400)
        
        user = User.query.get(user_id)
        if not user:
            return error('用户不存在', 404)
        
        # 检查用户名是否重复
        existing = User.query.filter_by(username=username).first()
        if existing and existing.id != user_id:
            return error('用户名已被占用', 400)
        
        user.username = username
        db.session.commit()
        
        return success({'username': user.username}, '用户名修改成功')
    
    # ========== 修改手机号 ==========
    @app.route('/api/auth/update-phone', methods=['POST'])
    def update_phone():
        """修改手机号"""
        data = request.get_json()
        
        user_id = data.get('user_id')
        new_phone = data.get('new_phone', '').strip()
        password = data.get('password', '')
        
        if not user_id:
            return error('缺少用户ID', 400)
        if not new_phone:
            return error('请输入新手机号', 400)
        if not re.match(r'^1[3-9]\d{9}$', new_phone):
            return error('请输入正确的手机号', 400)
        if not password:
            return error('请输入密码', 400)
        
        user = User.query.get(user_id)
        if not user:
            return error('用户不存在', 404)
        
        # 验证密码
        hashed_password = hashlib.md5(password.encode()).hexdigest()
        if user.password != hashed_password:
            return error('密码错误', 401)
        
        # 检查新手机号是否已被使用
        existing = User.query.filter_by(phone=new_phone).first()
        if existing and existing.id != user_id:
            return error('该手机号已被其他账号绑定', 400)
        
        user.phone = new_phone
        db.session.commit()
        
        return success({'phone': user.phone}, '手机号修改成功')
    
    # ========== 修改密码 ==========
    @app.route('/api/auth/update-password', methods=['POST'])
    def update_password():
        """修改密码"""
        data = request.get_json()
        
        user_id = data.get('user_id')
        old_password = data.get('old_password', '')
        new_password = data.get('new_password', '')
        
        if not user_id:
            return error('缺少用户ID', 400)
        if not old_password or not new_password:
            return error('请输入原密码和新密码', 400)
        if len(new_password) < 6:
            return error('新密码长度不能小于6位', 400)
        
        user = User.query.get(user_id)
        if not user:
            return error('用户不存在', 404)
        
        # 验证原密码
        hashed_old = hashlib.md5(old_password.encode()).hexdigest()
        if user.password != hashed_old:
            return error('原密码错误', 401)
        
        # 更新密码
        user.password = hashlib.md5(new_password.encode()).hexdigest()
        db.session.commit()
        
        return success(None, '密码修改成功，请重新登录')
    
    # ========== 修改头像 ==========
    @app.route('/api/auth/update-avatar', methods=['POST'])
    def update_avatar():
        """修改头像"""
        data = request.get_json()
        
        user_id = data.get('user_id')
        avatar = data.get('avatar', '')
        
        if not user_id:
            return error('缺少用户ID', 400)
        if not avatar:
            return error('头像地址不能为空', 400)
        
        user = User.query.get(user_id)
        if not user:
            return error('用户不存在', 404)
        
        user.avatar = avatar
        db.session.commit()
        
        return success({'avatar': user.avatar}, '头像修改成功')
    
    # ========== 获取用户完整资料 ==========
    @app.route('/api/auth/profile', methods=['GET'])
    def get_profile():
        """获取用户完整资料"""
        user_id = request.args.get('user_id', type=int)
        
        if not user_id:
            return error('缺少用户ID', 400)
        
        user = User.query.get(user_id)
        if not user:
            return error('用户不存在', 404)
        
        return success(user.to_dict())
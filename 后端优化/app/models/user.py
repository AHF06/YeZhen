from app.models.base import db, BaseModel
from datetime import datetime
import random
import string


class User(BaseModel):
    """用户模型"""
    __tablename__ = 'users'
    
    phone = db.Column(db.String(20), unique=True, nullable=False, index=True)  # 手机号
    password = db.Column(db.String(255), nullable=False)  # 密码（MD5加密）
    username = db.Column(db.String(50), unique=True, nullable=False)  # 用户名
    nickname = db.Column(db.String(50), default='农友')  # 昵称
    avatar = db.Column(db.String(255), default='')  # 头像
    openid = db.Column(db.String(100), unique=True, nullable=True)  # 微信openid
    
    def to_dict(self):
        return {
            'id': self.id,
            'phone': self.phone,
            'username': self.username,
            'nickname': self.nickname,
            'avatar': self.avatar,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }
    
    @staticmethod
    def generate_username():
        """生成随机用户名"""
        prefix = random.choice(['农夫', '田园', '丰收', '稻香', '麦浪', '果农', '菜友'])
        suffix = ''.join(random.choices(string.digits, k=4))
        return f"{prefix}{suffix}"
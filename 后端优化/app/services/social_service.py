import json
from flask import current_app
from app.models.base import db
from app.models.post import Post, PostLike, PostComment
from sqlalchemy import desc, func
from app.models.user import User 



class SocialService:
    """农友圈服务"""
    
    def create_post(self, user_id, content, images=None, crop_type=None, 
                    disease_name=None, location=None):
        """发布帖子"""
        print(f"create_post 接收到的 images: {images}")  # 调试
        images_json = json.dumps(images, ensure_ascii=False) if images else None
        print(f"保存的 images_json: {images_json}")  # 调试
        post = Post(
            user_id=user_id,
            content=content,
            images=images_json,
            crop_type=crop_type,
            disease_name=disease_name,
            location=location
        )
        post.save()
        return post
    

    def get_post_list(self, page=1, page_size=10, crop_type=None, disease_name=None, user_id=None, current_user_id=None):
        """获取帖子列表，关联用户信息"""
        query = Post.query
        
        if crop_type:
            query = query.filter(Post.crop_type == crop_type)
        if disease_name:
            query = query.filter(Post.disease_name.like(f'%{disease_name}%'))
        if user_id:
            query = query.filter(Post.user_id == user_id)
        
        query = query.order_by(desc(Post.created_at))
        pagination = query.paginate(page=page, per_page=page_size, error_out=False)
        
        posts = pagination.items
        user_ids = list(set([post.user_id for post in posts]))
        
        # 批量查询用户信息
        users = User.query.filter(User.id.in_(user_ids)).all() 
        user_map = {user.id: user for user in users}
        
        items = []
        for post in posts:
            user = user_map.get(post.user_id)
            items.append({
                'id': post.id,
                'user_id': post.user_id,
                'username': user.nickname if user else f'用户{post.user_id}',  # 使用昵称
                'avatar': user.avatar if user else '',
                'type': 'experience' if post.crop_type else 'question',
                'content': post.content,
                'crop_type': post.crop_type,
                'disease_name': post.disease_name,
                'images': json.loads(post.images) if post.images else [],
                'like_count': post.like_count,
                'comment_count': post.comment_count,
                'created_at': post.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'location': post.location
            })
        
        return {
            'total': pagination.total,
            'page': page,
            'page_size': page_size,
            'pages': pagination.pages,
            'items': items
        }
        
    def get_post_detail(self, post_id, current_user_id=None):
        """获取帖子详情"""
        post = Post.query.get(post_id)
        if not post:
            return None
        
        # 获取用户信息
        user = User.query.get(post.user_id)
        
        return {
            'id': post.id,
            'user_id': post.user_id,
            'username': user.nickname if user else f'用户{post.user_id}',
            'avatar': user.avatar if user else '',
            'type': 'experience' if post.crop_type else 'question',
            'content': post.content,
            'crop_type': post.crop_type,
            'disease_name': post.disease_name,
            'images': json.loads(post.images) if post.images else [],
            'like_count': post.like_count,
            'comment_count': post.comment_count,
            'created_at': post.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'location': post.location
        }
    
    def like_post(self, post_id, user_id):
        """点赞帖子"""
        # 检查是否已点赞
        existing = PostLike.query.filter_by(post_id=post_id, user_id=user_id).first()
        if existing:
            return False, '已经点过赞了'
        
        # 添加点赞记录
        like = PostLike(post_id=post_id, user_id=user_id)
        db.session.add(like)
        
        # 更新帖子点赞数
        post = Post.query.get(post_id)
        if post:
            post.like_count += 1
        
        db.session.commit()
        return True, '点赞成功'
    
    def unlike_post(self, post_id, user_id):
        """取消点赞"""
        like = PostLike.query.filter_by(post_id=post_id, user_id=user_id).first()
        if not like:
            return False, '尚未点赞'
        
        db.session.delete(like)
        
        # 更新帖子点赞数
        post = Post.query.get(post_id)
        if post and post.like_count > 0:
            post.like_count -= 1
        
        db.session.commit()
        return True, '取消点赞成功'
    
    def check_liked(self, post_id, user_id):
        """检查用户是否点赞了帖子"""
        return PostLike.query.filter_by(post_id=post_id, user_id=user_id).first() is not None
    
    def add_comment(self, post_id, user_id, content):
        """添加评论"""
        comment = PostComment(post_id=post_id, user_id=user_id, content=content)
        db.session.add(comment)
        
        # 更新帖子评论数
        post = Post.query.get(post_id)
        if post:
            post.comment_count += 1
        
        db.session.commit()
        return comment
    
    def get_comments(self, post_id, page=1, page_size=20):
        """获取帖子的评论列表"""
        query = PostComment.query.filter_by(post_id=post_id).order_by(desc(PostComment.created_at))
        pagination = query.paginate(page=page, per_page=page_size, error_out=False)
        
        return {
            'total': pagination.total,
            'page': page,
            'page_size': page_size,
            'pages': pagination.pages,
            'items': pagination.items
        }
    
    def delete_post(self, post_id, user_id):
        """删除帖子（只能删除自己的）"""
        post = Post.query.filter_by(id=post_id, user_id=user_id).first()
        if not post:
            return False, '帖子不存在或无权删除'
        
        db.session.delete(post)
        db.session.commit()
        return True, '删除成功'
    
    def delete_comment(self, comment_id, user_id):
        """删除评论（只能删除自己的）"""
        # 确保 comment_id 是整数
        comment_id = int(comment_id)
        
        comment = PostComment.query.filter_by(id=comment_id, user_id=user_id).first()
        if not comment:
            return False, '评论不存在或无权删除'
        
        post_id = comment.post_id
        
        db.session.delete(comment)
        
        # 更新帖子评论数
        post = Post.query.get(post_id)
        if post and post.comment_count > 0:
            post.comment_count -= 1
        
        db.session.commit()
        return True, '删除成功'


# 单例
_social_service = None

def get_social_service():
    global _social_service
    if _social_service is None:
        _social_service = SocialService()
    return _social_service
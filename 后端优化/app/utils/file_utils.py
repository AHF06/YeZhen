import os
import uuid
from datetime import datetime
from werkzeug.utils import secure_filename
from flask import current_app


def allowed_file(filename):
    """检查文件格式是否允许"""
    allowed_extensions = {'png', 'jpg', 'jpeg', 'bmp', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions


def generate_filename(original_filename):
    """生成唯一文件名"""
    ext = original_filename.rsplit('.', 1)[1].lower() if '.' in original_filename else 'jpg'
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    unique_id = uuid.uuid4().hex[:8]
    return f"{unique_id}_{timestamp}.{ext}"


def get_date_path():
    """获取日期路径，例如: 2026/04/02"""
    return datetime.now().strftime('%Y/%m/%d')


def save_upload_file(file, subdir='uploads'):
    """
    保存上传的文件到 picture 目录
    返回: (relative_path, absolute_path, url_path)
    relative_path: 相对路径，如 'uploads/2026/05/20/abc.jpg'
    url_path: URL 访问路径，如 '/picture/uploads/2026/05/20/abc.jpg'
    """
    if not file or file.filename == '':
        return None, None, None

    if not allowed_file(file.filename):
        return None, None, None

    filename = generate_filename(file.filename)
    date_path = get_date_path()

    # 相对路径（不包含 picture/ 前缀）
    relative_path = os.path.join(subdir, date_path, filename).replace('\\', '/')

    picture_dir = current_app.config.get('PICTURE_DIR', '')
    absolute_dir = os.path.join(picture_dir, subdir, date_path)
    absolute_path = os.path.join(absolute_dir, filename)

    os.makedirs(absolute_dir, exist_ok=True)
    file.save(absolute_path)

    # URL 路径：前端用 baseUrl + url_path 访问
    url_path = f'/picture/{relative_path}'

    print(f"保存文件 - relative_path: {relative_path}, url_path: {url_path}")

    return relative_path, absolute_path, url_path
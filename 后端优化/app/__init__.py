from flask import Flask
from flask_cors import CORS
from werkzeug.exceptions import HTTPException
import os

from app.config import config_map, Config
from app.models.base import db
from app.utils.response import error, success
from app.utils.exceptions import BusinessException


def create_app(config_name='default'):
    # 指定静态文件夹为项目根目录下的 static
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    static_dir = os.path.join(base_dir, 'static')
    
    app = Flask(__name__, static_folder=static_dir, static_url_path='/static')
    
    config_class = config_map.get(config_name, Config)
    app.config.from_object(config_class)
    
    os.makedirs(Config.UPLOAD_DIR, exist_ok=True)
    os.makedirs(Config.ANNOTATED_DIR, exist_ok=True)
    
    CORS(app, supports_credentials=True)
    db.init_app(app)
    
    with app.app_context():
        db.create_all()
        print('✅ 数据库初始化完成')
    
    @app.errorhandler(BusinessException)
    def handle_business_exception(e):
        return error(e.message, e.code)
    
    @app.errorhandler(HTTPException)
    def handle_http_exception(e):
        return error(e.description, e.code)
    
    @app.errorhandler(Exception)
    def handle_general_exception(e):
        app.logger.error(f'未处理的异常: {e}', exc_info=True)
        return error('服务器内部错误', 500)
    
    @app.route('/api/health', methods=['GET'])
    def health_check():
        return success({'status': 'ok', 'message': '服务运行正常'})
    
    # 注册路由
    from app.api.upload import register_upload_routes
    register_upload_routes(app)
    
    from app.api.weather import register_weather_routes
    register_weather_routes(app)
    
    from app.api.history import register_history_routes  
    register_history_routes(app)  
    
    from app.api.chat import register_chat_routes  
    register_chat_routes(app)  
    
    from app.api.social import register_social_routes  
    register_social_routes(app)  
    
    from app.api.warning import register_warning_routes
    register_warning_routes(app)
    
    from app.api.auth import register_auth_routes
    register_auth_routes(app)
    
    from app.api.advice import register_advice_routes
    register_advice_routes(app)

    # 提供 picture 目录的静态文件访问
    from flask import send_from_directory
    import os as _os

    @app.route('/picture/<path:filename>')
    def serve_picture(filename):
        picture_dir = app.config.get('PICTURE_DIR', '')
        return send_from_directory(picture_dir, filename)

    return app
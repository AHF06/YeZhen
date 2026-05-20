import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
    
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = int(os.getenv('DB_PORT', 3306))
    DB_USER = os.getenv('DB_USER', 'root')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')
    DB_NAME = os.getenv('DB_NAME', 'crop_detect_db')
    
    SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
    
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    PICTURE_DIR = os.path.join(BASE_DIR, '..', '..', 'picture')
    STATIC_DIR = os.path.join(BASE_DIR, 'static')
    UPLOAD_DIR = os.path.join(PICTURE_DIR, 'uploads')
    ANNOTATED_DIR = os.path.join(PICTURE_DIR, 'annotated')
    
    API_BASE_URL = os.getenv('API_BASE_URL', 'http://localhost:5000')
    
    AMAP_API_KEY = os.getenv('AMAP_API_KEY', '')
    
    LLM_BASE_URL = os.getenv('LLM_BASE_URL', 'http://localhost:11434')
    LLM_MODEL = os.getenv('LLM_MODEL', 'qwen2.5')
    
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'bmp'}
    
    WEIGHTS_DIR = os.getenv('WEIGHTS_DIR', 'weights')
    
    MODEL_FILES = {
        'rice': 'rice.onnx',
        'corn': 'corn.onnx',
        'tomato': 'tomato.onnx',
        'strawberry': 'strawberry.onnx'
    }
    
    DEFAULT_CROP = 'rice'


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_ECHO = True


class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_ECHO = False


config_map = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
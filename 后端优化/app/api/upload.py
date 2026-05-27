# app/api/upload.py
from flask import request, current_app
from app.utils.response import success, error
from app.utils.file_utils import save_upload_file
from app.models.base import db
from app.models.detection_record import DetectionRecord
from app.services.detection_service import DetectionService
from app.services.weather_service import get_weather_service
import json


def register_upload_routes(app):

    @app.route('/api/upload', methods=['POST'])
    def upload_image():
        """图片上传并识别接口（同步识别，异步生成建议）"""
        if 'file' not in request.files:
            return error('请选择要上传的图片', 400)

        file = request.files['file']
        user_id = request.form.get('user_id', 0, type=int)
        crop_type_en = request.form.get('crop_type', 'rice')
        lat = request.form.get('lat')
        lon = request.form.get('lon')

        # 作物名映射（英文 -> 中文）
        CROP_NAME_MAP = {
            'rice': '水稻',
            'corn': '玉米',
            'tomato': '番茄',
            'strawberry': '草莓'
        }
        crop_type = CROP_NAME_MAP.get(crop_type_en, crop_type_en)

        # 保存文件到 picture 目录
        relative_path, absolute_path, url_path = save_upload_file(file)
        if relative_path is None:
            return error('不支持的文件格式', 400)

        # 执行病害识别（YOLO）
        detection_service = DetectionService()
        result = detection_service.recognize(absolute_path, crop_type_en)

        if not result['success']:
            return error(result['error_msg'], 500)

        detections = result['detections']
        annotated_path = result.get('annotated_path')

        if detections:
            main_disease = detections[0]['label']
            confidence = detections[0]['confidence']
        else:
            main_disease = '未检测到病害'
            confidence = 0.0

        # 获取天气信息
        location_weather = {}
        if lat and lon:
            try:
                weather_service = get_weather_service()
                weather_result = weather_service.get_weather_and_location(float(lat), float(lon))
                if weather_result.get('success'):
                    location_weather = {
                        'city': weather_result.get('city'),
                        'province': weather_result.get('province'),
                        'weather': weather_result.get('weather'),
                        'temperature': weather_result.get('temperature'),
                        'humidity': weather_result.get('humidity'),
                        'wind': weather_result.get('wind')
                    }
            except Exception as e:
                print(f"天气获取失败: {e}")

        # 转换标注图为 URL 路径
        annotated_url_path = None
        annotated_relative_path = None
        if annotated_path:
            picture_dir = current_app.config.get('PICTURE_DIR', '')
            # 从绝对路径提取相对路径部分
            if annotated_path.startswith(picture_dir):
                rel = annotated_path[len(picture_dir)+1:].replace('\\', '/')
                annotated_relative_path = rel
                annotated_url_path = f'/picture/{rel}'
            else:
                annotated_relative_path = annotated_path.replace('\\', '/')
                annotated_url_path = f'/picture/{annotated_relative_path}'

        # 保存记录到数据库（只存相对路径，不含 IP）
        record = DetectionRecord(
            user_id=user_id,
            image_path=relative_path,
            annotated_image_path=annotated_relative_path,
            crop_type=crop_type,
            disease_name=main_disease,
            confidence=confidence,
            bbox_info=json.dumps(detections, ensure_ascii=False) if detections else None,
            weather_info=json.dumps(location_weather, ensure_ascii=False) if location_weather else None,
            ai_advice=None
        )
        db.session.add(record)
        db.session.commit()

        # 返回结果——image_url 和 annotated_image_url 是 URL 路径，不含 IP
        return success({
            'record_id': record.id,
            'image_url': url_path,
            'annotated_image_url': annotated_url_path,
            'crop_type': crop_type,
            'disease_name': main_disease,
            'confidence': confidence,
            'detections': detections,
            'location_weather': location_weather,
            'ai_advice': None
        }, '识别成功')
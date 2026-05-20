# app/api/advice.py
from flask import request
from app.utils.response import success, error
from app.models.detection_record import DetectionRecord
from app.models.base import db
import json
import traceback

def register_advice_routes(app):
    
    @app.route('/api/advice/generate', methods=['POST'])
    def generate_advice_for_record():
        data = request.get_json()
        if not data:
            return error('请求体不能为空', 400)
        record_id = data.get('record_id')
        if not record_id:
            return error('缺少 record_id', 400)
        
        record = DetectionRecord.query.get(record_id)
        if not record:
            return error('记录不存在', 404)
        
        if record.ai_advice:
            return success({'ai_advice': record.ai_advice})
        
        # 准备调用 LLM 的参数
        crop_type = record.crop_type
        disease_name = record.disease_name
        confidence = record.confidence
        
        # 解析天气信息（可能为 None 或 JSON 字符串）
        weather_info = {}
        if record.weather_info:
            try:
                weather_info = json.loads(record.weather_info) if isinstance(record.weather_info, str) else record.weather_info
            except:
                weather_info = {}
        
        location_info = {}
        if weather_info.get('city'):
            location_info['city'] = weather_info.get('city')
            location_info['province'] = weather_info.get('province')
        
        # 导入 LLM 服务（延迟导入避免循环依赖）
        from app.services.llm_service import generate_advice
        advice_result = generate_advice(crop_type, disease_name, confidence, weather_info, location_info)
        
        if advice_result.get('success'):
            ai_advice = advice_result['advice']
            try:
                record.ai_advice = ai_advice
                db.session.commit()
                return success({'ai_advice': ai_advice})
            except Exception as e:
                db.session.rollback()
                app.logger.error(f"数据库更新失败: {e}")
                return error('保存建议失败', 500)
        else:
            err_msg = advice_result.get('error', '生成失败')
            return error(err_msg, 500)
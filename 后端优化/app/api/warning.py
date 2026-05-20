from flask import request
from app.utils.response import success, error
from app.services.weather_service import get_weather_service
from app.services.disease_predictor import DiseasePredictor
from app.services.region_warning_service import get_region_service


def register_warning_routes(app):
    
    # ========== 天气预警（基于实时天气预测） ==========
    @app.route('/api/warning/weather', methods=['GET'])
    def get_weather_warning():
        """
        根据天气预测病害
        
        参数:
            lat: 纬度
            lon: 经度
            crop_type: 作物类型 (rice/corn/tomato/strawberry)
        """
        lat = request.args.get('lat')
        lon = request.args.get('lon')
        crop_type = request.args.get('crop_type', 'rice')
        
        if not lat or not lon:
            return error('缺少经纬度参数', 400)
        
        try:
            lat = float(lat)
            lon = float(lon)
        except ValueError:
            return error('经纬度格式错误', 400)
        
        # 获取天气数据
        weather_service = get_weather_service()
        weather_data = weather_service.get_weather_and_location(lat, lon)
        
        if not weather_data.get('success'):
            return error(weather_data.get('error', '获取天气失败'), 500)
        
        # 预测病害
        predictor = DiseasePredictor()
        predictions = predictor.predict_by_weather(
            crop_type=crop_type,
            weather=weather_data.get('weather', ''),
            temperature=int(weather_data.get('temperature', 22)),
            humidity=int(weather_data.get('humidity', 65))
        )
        
        # 计算整体风险等级
        risk_level = '低风险'
        if predictions:
            high_count = sum(1 for p in predictions if p['risk'] == '高危')
            if high_count >= 1:
                risk_level = '高危'
            elif any(p['risk'] == '中危' for p in predictions):
                risk_level = '中风险'
        
        return success({
            'location': weather_data.get('city'),
            'weather': {
                'weather': weather_data.get('weather'),
                'temperature': weather_data.get('temperature'),
                'humidity': weather_data.get('humidity')
            },
            'predictions': predictions,
            'risk_level': risk_level,
            'crop_type': crop_type,
            'update_time': predictor._get_current_time()
        })
    
    
    @app.route('/api/warning/all-regions', methods=['GET'])
    def get_all_regions_warning():
        """获取所有七大区域的病害预警"""
        service = get_region_service()
        results = service.get_all_regions_warning()
        return success(results)
    
    # ========== 作物列表 ==========
    @app.route('/api/warning/crops', methods=['GET'])
    def get_crops():
        """获取支持的作物列表"""
        return success({
            'crops': [
                {'value': 'rice', 'label': '水稻'},
                {'value': 'corn', 'label': '玉米'},
                {'value': 'tomato', 'label': '番茄'},
                {'value': 'strawberry', 'label': '草莓'}
            ]
        })
    
    # ========== 区域列表 ==========
    @app.route('/api/warning/region', methods=['GET'])
    def get_region_warning():
        """获取指定区域的病害预警"""
        region = request.args.get('region', '华东')
        
        service = get_region_service()
        result = service.get_region_warning(region)
        
        if not result:
            return error('区域不存在', 400)
        
        # 如果有错误，返回错误信息
        if result.get('error'):
            return error(result['error'], 500)
        
        return success({
            'region': result['region'],
            'cities': result['cities'],
            'climate': result['climate'],
            'analysis': result['analysis'],
            'update_time': result['update_time']
        })
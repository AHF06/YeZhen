import requests
from datetime import datetime
from flask import current_app


class WeatherService:
    """天气服务类 - 为AI提供上下文信息"""
    
    def __init__(self):
        self.api_key = None
        
    def _get_api_key(self):
        if self.api_key is None:
            self.api_key = current_app.config.get('AMAP_API_KEY', '')
        return self.api_key
    
    # 在 WeatherService 类中添加以下方法

    def get_disease_forecast(self, lat, lon, crop_type='rice'):
        """
        根据天气获取病害预警
        
        参数:
            lat: 纬度
            lon: 经度
            crop_type: 作物类型 (rice/corn/tomato/strawberry)
        
        返回:
            {
                'success': bool,
                'location': str,
                'weather': dict,
                'warnings': list,  # 预警列表
                'risk_level': str  # 风险等级
            }
        """
        # 1. 获取天气和位置
        weather_data = self.get_weather_and_location(lat, lon)
        
        if not weather_data.get('success'):
            return {
                'success': False,
                'error': weather_data.get('error', '获取天气失败')
            }
        
        # 2. 解析天气数据
        weather = weather_data.get('weather', '')
        temperature = int(weather_data.get('temperature', 22))
        humidity = int(weather_data.get('humidity', 60))
        
        # 3. 判断天气条件
        from .disease_forecast import get_weather_condition, WEATHER_DISEASE_RULES
        
        weather_condition = get_weather_condition(weather, temperature, humidity)
        
        # 4. 获取对应作物的病害预警
        crop_rules = WEATHER_DISEASE_RULES.get(crop_type, WEATHER_DISEASE_RULES.get('rice', {}))
        
        warnings = []
        for condition, diseases in crop_rules.items():
            if condition in weather_condition or condition == weather_condition:
                for disease in diseases:
                    warnings.append({
                        'disease': disease,
                        'condition': condition,
                        'risk': self._get_risk_level(condition),
                        'advice': self._get_prevent_advice(disease, condition)
                    })
        
        # 5. 计算风险等级
        risk_level = self._calculate_risk_level(warnings, weather_condition)
        
        return {
            'success': True,
            'location': weather_data.get('city'),
            'weather': {
                'weather': weather,
                'temperature': temperature,
                'humidity': humidity,
                'condition': weather_condition
            },
            'warnings': warnings,
            'risk_level': risk_level,
            'update_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

    def _get_risk_level(self, condition):
        """根据天气条件获取风险等级"""
        risk_map = {
            '高温高湿': '高危',
            '低温阴雨': '高危',
            '多雨': '中危',
            '台风暴雨': '高危',
            '高温': '中危',
            '高湿': '中危'
        }
        return risk_map.get(condition, '低危')

    def _get_prevent_advice(self, disease, condition):
        """获取防治建议"""
        advice_map = {
            '稻瘟病': '注意田间排水，降低湿度，可喷施三环唑预防',
            '纹枯病': '合理密植，增施磷钾肥，发病初期用井冈霉素',
            '稻曲病': '抽穗期避开雨天，可喷施戊唑醇',
            '白叶枯病': '避免深灌，发病初期用叶枯唑',
            '晚疫病': '加强通风，降低湿度，喷施代森锰锌',
            '灰霉病': '及时摘除病叶，用嘧霉胺防治'
        }
        return advice_map.get(disease, '加强田间巡查，及时防治')
        
    def _calculate_risk_level(self, warnings, weather_condition):
        """计算整体风险等级"""
        if not warnings:
            return '低危'
        
        high_risk_count = sum(1 for w in warnings if w['risk'] == '高危')
        if high_risk_count >= 2 or weather_condition in ['高温高湿', '低温阴雨']:
            return '高危'
        elif high_risk_count >= 1:
            return '中危'
        return '低危'
    
    def get_weather_and_location(self, lat, lon):
        """
        根据经纬度获取天气和地区信息（用于AI上下文）
        
        参数:
            lat: 纬度
            lon: 经度
            
        返回:
            {
                'success': bool,
                'city': str,        # 城市名
                'province': str,    # 省份
                'weather': str,     # 天气状况（如：晴、多云、小雨）
                'temperature': str, # 当前温度（或温度范围）
                'humidity': str,    # 湿度
                'wind': str         # 风力
            }
        """
        api_key = self._get_api_key()
        
        if not api_key:
            return {
                'success': False,
                'error': '未配置高德API Key'
            }
        
        try:
            # 1. 通过经纬度获取城市信息
            geo_url = "https://restapi.amap.com/v3/geocode/regeo"
            geo_params = {
                "key": api_key,
                "location": f"{lon},{lat}",
                "extensions": "base"
            }
            
            geo_resp = requests.get(geo_url, params=geo_params, timeout=5)
            geo_data = geo_resp.json()
            
            if geo_data.get('status') != '1':
                return {
                    'success': False,
                    'error': f"地理编码失败: {geo_data.get('info', '未知错误')}"
                }
            
            # 提取城市信息
            address_component = geo_data.get('regeocode', {}).get('addressComponent', {})
            city = address_component.get('city', '')
            province = address_component.get('province', '')
            
            # 直辖市处理（如北京、上海）
            if not city:
                city = province
            
            # 获取adcode用于天气查询
            adcode = address_component.get('adcode', '')
            
            # 2. 获取天气信息
            weather_url = "https://restapi.amap.com/v3/weather/weatherInfo"
            weather_params = {
                "key": api_key,
                "city": adcode,
                "extensions": "base",  # base=实时天气，all=预报
                "output": "json"
            }
            
            weather_resp = requests.get(weather_url, params=weather_params, timeout=5)
            weather_data = weather_resp.json()
            
            if weather_data.get('status') != '1':
                return {
                    'success': False,
                    'city': city,
                    'province': province,
                    'weather': '未知',
                    'temperature': '未知',
                    'humidity': '未知',
                    'wind': '未知'
                }
            
            # 提取实时天气
            lives = weather_data.get('lives', [])
            if lives:
                live = lives[0]
                return {
                    'success': True,
                    'city': live.get('city', city),
                    'province': province,
                    'weather': live.get('weather', '未知'),
                    'temperature': live.get('temperature', '未知'),
                    'humidity': live.get('humidity', '未知'),
                    'wind': live.get('winddirection', '未知') + live.get('windpower', '') + '级'
                }
            else:
                return {
                    'success': False,
                    'city': city,
                    'province': province,
                    'weather': '未知',
                    'temperature': '未知',
                    'humidity': '未知',
                    'wind': '未知'
                }
                
        except requests.exceptions.Timeout:
            return {
                'success': False,
                'error': '请求超时'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }


    def get_forecast(self, lat, lon):
        """
        获取未来天气预报（4天）

        返回:
            {
                'success': bool,
                'city': str,
                'forecasts': [{
                    'date': str,
                    'week': str,
                    'dayweather': str,
                    'nightweather': str,
                    'daytemp': str,
                    'nighttemp': str,
                    'daywind': str,
                    'nightwind': str,
                }, ...]
            }
        """
        api_key = self._get_api_key()

        if not api_key:
            return {'success': False, 'error': '未配置高德API Key'}

        try:
            # 先获取城市
            geo_url = "https://restapi.amap.com/v3/geocode/regeo"
            geo_params = {
                "key": api_key,
                "location": f"{lon},{lat}",
                "extensions": "base"
            }
            geo_resp = requests.get(geo_url, params=geo_params, timeout=5)
            geo_data = geo_resp.json()

            if geo_data.get('status') != '1':
                return {'success': False, 'error': '地理编码失败'}

            address_component = geo_data.get('regeocode', {}).get('addressComponent', {})
            city = address_component.get('city', '')
            province = address_component.get('province', '')
            if not city:
                city = province
            adcode = address_component.get('adcode', '')

            # 获取天气预报
            weather_url = "https://restapi.amap.com/v3/weather/weatherInfo"
            weather_params = {
                "key": api_key,
                "city": adcode,
                "extensions": "all",
                "output": "json"
            }
            weather_resp = requests.get(weather_url, params=weather_params, timeout=5)
            weather_data = weather_resp.json()

            if weather_data.get('status') != '1':
                return {'success': False, 'error': '获取预报失败'}

            forecasts_list = weather_data.get('forecasts', [])
            if forecasts_list:
                return {
                    'success': True,
                    'city': forecasts_list[0].get('city', city),
                    'forecasts': forecasts_list[0].get('casts', [])
                }

            return {'success': False, 'error': '无预报数据'}

        except requests.exceptions.Timeout:
            return {'success': False, 'error': '请求超时'}
        except Exception as e:
            return {'success': False, 'error': str(e)}


# 单例
_weather_service = None

def get_weather_service():
    global _weather_service
    if _weather_service is None:
        _weather_service = WeatherService()
    return _weather_service
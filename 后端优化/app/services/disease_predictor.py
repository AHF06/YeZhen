# app/services/disease_predictor.py
from datetime import datetime


class DiseasePredictor:
    """病害预测服务"""
    
    # 天气条件与病害的关系规则
    WEATHER_DISEASE_RULES = {
        'rice': {  # 水稻
            '高温高湿': [
                {'disease': '稻瘟病', 'risk': '高危', 'advice': '喷施三环唑或稻瘟灵，间隔7天一次'},
                {'disease': '纹枯病', 'risk': '高危', 'advice': '使用井冈霉素，注意田间排水'},
                {'disease': '稻曲病', 'risk': '中危', 'advice': '抽穗期喷施戊唑醇，避开雨天'}
            ],
            '多雨': [
                {'disease': '白叶枯病', 'risk': '中危', 'advice': '使用叶枯唑，避免深灌'},
                {'disease': '细菌性条斑病', 'risk': '中危', 'advice': '喷施噻菌铜，加强田间管理'}
            ],
            '低温阴雨': [
                {'disease': '恶苗病', 'risk': '中危', 'advice': '种子消毒，喷施多菌灵'},
                {'disease': '立枯病', 'risk': '低危', 'advice': '注意保温，喷施恶霉灵'}
            ],
            '台风暴雨': [
                {'disease': '稻飞虱', 'risk': '高危', 'advice': '使用吡蚜酮，注意轮换用药'},
                {'disease': '细菌性病害', 'risk': '高危', 'advice': '风雨后及时喷施杀菌剂'}
            ]
        },
        'corn': {  # 玉米
            '高温高湿': [
                {'disease': '大斑病', 'risk': '高危', 'advice': '喷施吡唑醚菌酯或戊唑醇'},
                {'disease': '小斑病', 'risk': '高危', 'advice': '使用代森锰锌或百菌清'},
                {'disease': '锈病', 'risk': '中危', 'advice': '喷施三唑酮或烯唑醇'}
            ],
            '干旱': [
                {'disease': '玉米螟', 'risk': '中危', 'advice': '释放赤眼蜂，或喷施氯虫苯甲酰胺'},
                {'disease': '蚜虫', 'risk': '中危', 'advice': '喷施吡虫啉，保护天敌'},
                {'disease': '红蜘蛛', 'risk': '低危', 'advice': '喷施阿维菌素'}
            ],
            '多雨': [
                {'disease': '茎腐病', 'risk': '中危', 'advice': '注意排水，喷施甲霜灵'},
                {'disease': '穗腐病', 'risk': '中危', 'advice': '及时收获，避免雨水淋湿'}
            ]
        },
        'tomato': {  # 番茄
            '高温高湿': [
                {'disease': '晚疫病', 'risk': '高危', 'advice': '使用代森锰锌或霜脲氰'},
                {'disease': '早疫病', 'risk': '高危', 'advice': '喷施百菌清或异菌脲'},
                {'disease': '叶霉病', 'risk': '中危', 'advice': '加强通风，喷施春雷霉素'}
            ],
            '多雨': [
                {'disease': '灰霉病', 'risk': '中危', 'advice': '使用嘧霉胺或腐霉利'},
                {'disease': '炭疽病', 'risk': '中危', 'advice': '喷施咪鲜胺或苯醚甲环唑'}
            ],
            '低温': [
                {'disease': '病毒病', 'risk': '中危', 'advice': '防治蚜虫，喷施宁南霉素'}
            ]
        },
        'strawberry': {  # 草莓
            '高湿': [
                {'disease': '灰霉病', 'risk': '高危', 'advice': '使用嘧霉胺，降低湿度'},
                {'disease': '白粉病', 'risk': '高危', 'advice': '喷施三唑酮或醚菌酯'},
                {'disease': '炭疽病', 'risk': '中危', 'advice': '喷施咪鲜胺，及时清理病叶'}
            ],
            '多雨': [
                {'disease': '根腐病', 'risk': '中危', 'advice': '注意排水，灌根恶霉灵'},
                {'disease': '叶斑病', 'risk': '低危', 'advice': '喷施代森锰锌'}
            ]
        }
    }
    
    def get_weather_condition(self, weather, temperature, humidity):
        """判断天气条件"""
        # 温度判断
        if temperature > 28:
            is_high_temp = True
        else:
            is_high_temp = False
        
        # 湿度判断
        is_high_humidity = humidity > 85
        
        # 天气判断
        if '雨' in weather:
            if '暴雨' in weather or '大暴雨' in weather:
                return '台风暴雨'
            return '多雨'
        elif is_high_temp and is_high_humidity:
            return '高温高湿'
        elif is_high_humidity:
            return '高湿'
        elif is_high_temp:
            return '高温'
        
        return '正常'
    
    def predict_by_weather(self, crop_type, weather, temperature, humidity):
        """根据天气预测病害"""
        condition = self.get_weather_condition(weather, temperature, humidity)
        
        rules = self.WEATHER_DISEASE_RULES.get(crop_type, {})
        predictions = rules.get(condition, [])
        
        # 添加天气条件说明
        for p in predictions:
            p['condition'] = condition
        
        return predictions
    
    def _get_current_time(self):
        """获取当前时间"""
        from datetime import datetime
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')
# 天气条件与病害的关联规则
WEATHER_DISEASE_RULES = {
    'rice': {  # 水稻
        '高温高湿': ['稻瘟病', '纹枯病', '稻曲病'],
        '多雨': ['白叶枯病', '细菌性条斑病'],
        '低温阴雨': ['恶苗病', '立枯病'],
        '台风暴雨': ['细菌性病害', '稻飞虱']
    },
    'corn': {  # 玉米
        '高温高湿': ['大斑病', '小斑病', '锈病'],
        '干旱': ['玉米螟', '蚜虫'],
        '多雨': ['茎腐病', '穗腐病']
    },
    'tomato': {  # 番茄
        '高温高湿': ['晚疫病', '早疫病'],
        '多雨': ['叶霉病', '灰霉病'],
        '低温': ['病毒病']
    },
    'strawberry': {  # 草莓
        '高湿': ['灰霉病', '白粉病'],
        '多雨': ['炭疽病', '根腐病']
    }
}

# 天气条件判断函数
def get_weather_condition(weather, temperature, humidity):
    """根据天气数据判断天气类型"""
    conditions = []
    
    # 温度判断
    if temperature > 28:
        conditions.append('高温')
    elif temperature < 15:
        conditions.append('低温')
    
    # 湿度判断
    if humidity > 85:
        conditions.append('高湿')
    elif humidity > 70:
        conditions.append('中湿')
    
    # 天气判断
    if '雨' in weather:
        conditions.append('多雨')
    elif '雷阵雨' in weather or '暴雨' in weather:
        conditions.append('台风暴雨')
    
    # 组合条件
    if '高温' in conditions and '高湿' in conditions:
        return '高温高湿'
    elif '低温' in conditions and '雨' in weather:
        return '低温阴雨'
    elif '多雨' in conditions:
        return '多雨'
    elif '高温' in conditions:
        return '高温'
    elif '高湿' in conditions:
        return '高湿'
    
    return '正常'
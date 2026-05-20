# app/services/region_warning_service.py
import requests
import json
import re
from flask import current_app
from datetime import datetime


class RegionWarningService:
    """区域预警服务 - 基于AI实时分析"""
    
    # 七大地理分区及特点
    REGIONS = {
        '华东': {
            'cities': ['上海', '江苏', '浙江', '安徽', '福建', '江西', '山东'],
            'climate': '亚热带季风气候，夏季高温多雨，冬季温和少雨',
            'features': '水稻主产区，病虫害发生频繁'
        },
        '华南': {
            'cities': ['广东', '广西', '海南'],
            'climate': '热带/亚热带季风气候，全年高温多雨，湿度大',
            'features': '常年高温高湿，病虫害高发区'
        },
        '华中': {
            'cities': ['河南', '湖北', '湖南'],
            'climate': '亚热带季风气候，四季分明，雨热同期',
            'features': '水稻、小麦主产区'
        },
        '华北': {
            'cities': ['北京', '天津', '河北', '山西', '内蒙古'],
            'climate': '温带季风气候，春季干旱多风，夏季炎热多雨',
            'features': '玉米、小麦主产区，春季干旱严重'
        },
        '西南': {
            'cities': ['重庆', '四川', '贵州', '云南', '西藏'],
            'climate': '高原山地气候，立体气候明显，多雨多雾',
            'features': '地形复杂，病害种类多样'
        },
        '西北': {
            'cities': ['陕西', '甘肃', '青海', '宁夏', '新疆'],
            'climate': '温带大陆性气候，干旱少雨，昼夜温差大',
            'features': '灌溉农业区，病害相对较少'
        },
        '东北': {
            'cities': ['辽宁', '吉林', '黑龙江'],
            'climate': '温带季风气候，冬季寒冷漫长，夏季温暖短促',
            'features': '玉米、大豆主产区，春播期低温病害多'
        }
    }
    
    # 作物类型
    CROPS = ['水稻', '玉米', '番茄', '草莓']
    
    def __init__(self):
        self.llm_url = None
        self.llm_model = None
    
    def _get_llm_config(self):
        """获取LLM配置"""
        if self.llm_url is None:
            self.llm_url = current_app.config.get('LLM_BASE_URL', 'http://localhost:11434')
            self.llm_model = current_app.config.get('LLM_MODEL', 'qwen2.5')
        return self.llm_url, self.llm_model
    
    def get_region_warning(self, region_name):
        """
        获取指定区域的病害预警（AI实时分析）
        """
        if region_name not in self.REGIONS:
            return None
        
        region_info = self.REGIONS[region_name]
        cities = region_info['cities']
        climate = region_info['climate']
        features = region_info['features']
        
        # 构建AI提示词
        prompt = self._build_prompt(region_name, cities, climate, features)
        
        # 调用AI分析
        analysis, error = self._call_llm(prompt, region_name)
        
        return {
            'region': region_name,
            'cities': cities,
            'climate': climate,
            'analysis': analysis,
            'error': error,
            'update_time': self._get_current_time()
        }
    
    def _build_prompt(self, region_name, cities, climate, features):
        """构建AI提示词"""
        crops_text = '、'.join(self.CROPS)
        cities_text = '、'.join(cities[:5])
        
        return f'''你是一位农业病虫害预警专家。请根据以下信息，分析{region_name}地区当前的病虫害风险。

【地区信息】
- 地区：{region_name}
- 主要城市：{cities_text}等
- 气候特点：{climate}
- 农业特点：{features}
- 当前季节：{self._get_current_season()}
- 主要作物：{crops_text}

请针对每种作物，预测当前季节最容易发生的2-3种病害，按以下JSON格式输出：

{{
    "rice": [
        {{"disease": "病害名称", "risk": "高风险/中风险/低风险", "reason": "发生原因", "advice": "防治建议"}}
    ],
    "corn": [],
    "tomato": [],
    "strawberry": []
}}

要求：
1. 必须结合该地区的气候特点和农业特点
2. 风险等级：高风险/中风险/低风险
3. 原因要符合该地区的实际情况
4. 防治建议要具体可操作
5. 只输出JSON，不要有其他文字'''
    
    def _call_llm(self, prompt, region_name):
        """调用LLM分析，失败时返回错误"""
        llm_url, llm_model = self._get_llm_config()
        
        payload = {
            "model": llm_model,
            "messages": [
                {
                    "role": "system",
                    "content": "你是一位农业病虫害预警专家，擅长根据地区气候特点预测病害风险。请只输出JSON格式，不要有其他文字。"
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "stream": False,
            "temperature": 0.6
        }
        
        try:
            api_url = f"{llm_url}/api/chat"
            print(f"正在调用AI分析{region_name}地区...")
            response = requests.post(api_url, json=payload, timeout=60)
            
            if response.status_code == 200:
                result = response.json()
                content = result.get('message', {}).get('content', '')
                print(f"AI返回成功")
                parsed_data, parse_error = self._parse_response(content)
                if parse_error:
                    return None, parse_error
                return parsed_data, None
            else:
                error_msg = f"AI服务请求失败: HTTP {response.status_code}"
                print(error_msg)
                return None, error_msg
                
        except requests.exceptions.Timeout:
            error_msg = "AI服务响应超时，请稍后重试"
            print(error_msg)
            return None, error_msg
        except requests.exceptions.ConnectionError:
            error_msg = "无法连接AI服务，请检查Ollama是否运行"
            print(error_msg)
            return None, error_msg
        except Exception as e:
            error_msg = f"AI服务异常: {str(e)}"
            print(error_msg)
            return None, error_msg
    
    def _parse_response(self, content):
        """解析LLM返回的JSON"""
        try:
            # 尝试提取JSON部分
            json_match = re.search(r'\{[\s\S]*\}', content)
            if json_match:
                json_str = json_match.group()
                data = json.loads(json_str)
                
                # 确保所有作物都有字段
                for crop_key in ['rice', 'corn', 'tomato', 'strawberry']:
                    if crop_key not in data:
                        data[crop_key] = []
                
                return data, None
            else:
                return None, "AI返回格式错误，未找到有效JSON"
        except Exception as e:
            return None, f"解析AI响应失败: {str(e)}"
    
    def _get_current_season(self):
        """获取当前季节"""
        month = datetime.now().month
        if 3 <= month <= 5:
            return '春季'
        elif 6 <= month <= 8:
            return '夏季'
        elif 9 <= month <= 11:
            return '秋季'
        else:
            return '冬季'
    
    def _get_current_time(self):
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')


_region_service = None

def get_region_service():
    global _region_service
    if _region_service is None:
        _region_service = RegionWarningService()
    return _region_service
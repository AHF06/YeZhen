from flask import request, current_app
from app.utils.response import success, error
from app.services.history_service import get_history_service
from app.models.detection_record import DetectionRecord
import json


def register_history_routes(app):
    
    @app.route('/api/history/list', methods=['GET'])
    def get_history_list():
        """
        获取历史记录列表
        """
        user_id = request.args.get('user_id', type=int)
        
        if user_id is None:
            return error('缺少用户ID', 400)
        
        page = request.args.get('page', 1, type=int)
        page_size = request.args.get('page_size', 10, type=int)
        crop_type = request.args.get('crop_type')
        disease_name = request.args.get('disease_name')
        
        if page_size > 50:
            page_size = 50
        
        service = get_history_service()
        result = service.get_list(user_id, page, page_size, crop_type, disease_name)
        # 返回 URL 路径（不含 IP，前端自行拼接）
        items = []
        for record in result['items']:
            # 原图 URL 路径
            img_path = record.image_path.replace('\\', '/') if record.image_path else ''
            image_url = f'/picture/{img_path}' if img_path else None
            # 标注图 URL 路径
            annotated_url = None
            if record.annotated_image_path:
                ann_path = record.annotated_image_path.replace('\\', '/')
                annotated_url = f'/picture/{ann_path}'
                        
            items.append({
                'id': record.id,
                'user_id': record.user_id,
                'image_url': image_url,
                'annotated_image_url': annotated_url,
                'crop_type': record.crop_type,
                'disease_name': record.disease_name,
                'confidence': record.confidence,
                'detections': json.loads(record.bbox_info) if record.bbox_info else [],
                'weather_info': json.loads(record.weather_info) if record.weather_info else {},
                'ai_advice': record.ai_advice,
                'status': record.status,
                'created_at': record.created_at.strftime('%Y-%m-%d %H:%M:%S')
            })

        return success({
            'total': result['total'],
            'page': result['page'],
            'page_size': result['page_size'],
            'pages': result['pages'],
            'items': items
        })
    
    @app.route('/api/history/detail/<int:record_id>', methods=['GET'])
    def get_history_detail(record_id):
        """
        获取单条记录详情
        """
        user_id = request.args.get('user_id', type=int)
        
        if user_id is None:
            return error('缺少用户ID', 400)
        
        service = get_history_service()
        record = service.get_detail(record_id, user_id)

        if not record:
            return error('记录不存在', 404)

        # URL 路径（不含 IP，前端自行拼接）
        img_path = record.image_path.replace('\\', '/') if record.image_path else ''
        image_url = f'/picture/{img_path}' if img_path else None

        annotated_url = None
        if record.annotated_image_path:
            ann_path = record.annotated_image_path.replace('\\', '/')
            annotated_url = f'/picture/{ann_path}'
        
        return success({
            'id': record.id,
            'user_id': record.user_id,
            'image_url': image_url,
            'annotated_image_url': annotated_url,
            'crop_type': record.crop_type,
            'disease_name': record.disease_name,
            'confidence': record.confidence,
            'detections': json.loads(record.bbox_info) if record.bbox_info else [],
            'weather_info': json.loads(record.weather_info) if record.weather_info else {},
            'ai_advice': record.ai_advice,
            'status': record.status,
            'created_at': record.created_at.strftime('%Y-%m-%d %H:%M:%S')
        })

    @app.route('/api/history/delete/<int:record_id>', methods=['DELETE'])
    def delete_history_record(record_id):
        """
        删除记录
        """
        user_id = request.args.get('user_id', type=int)
        
        if not user_id:
            data = request.get_json() if request.is_json else {}
            user_id = data.get('user_id')
        
        print(f"删除记录 - record_id: {record_id}, user_id: {user_id}")
        
        if user_id is None:
            return error('缺少用户ID', 400)
        
        service = get_history_service()
        success_flag, message = service.delete_record(record_id, user_id)
        
        if success_flag:
            return success(None, message)
        else:
            return error(message, 400)
    
    @app.route('/api/history/statistics', methods=['GET'])
    def get_history_statistics():
        """
        获取用户统计信息
        """
        user_id = request.args.get('user_id', type=int)
        
        if user_id is None:
            return error('缺少用户ID', 400)
        
        service = get_history_service()
        statistics = service.get_statistics(user_id)
        
        return success(statistics)
    
    @app.route('/api/history/batch-delete', methods=['POST'])
    def batch_delete_records():
        """
        批量删除记录
        """
        data = request.get_json()
        
        if not data:
            return error('请求体不能为空', 400)
        
        user_id = data.get('user_id')
        record_ids = data.get('record_ids', [])
        
        if user_id is None:
            return error('缺少用户ID', 400)
        
        if not record_ids:
            return error('请选择要删除的记录', 400)
        
        service = get_history_service()
        success_count = 0
        fail_count = 0
        
        for record_id in record_ids:
            success_flag, _ = service.delete_record(record_id, user_id)
            if success_flag:
                success_count += 1
            else:
                fail_count += 1
        
        return success({
            'success_count': success_count,
            'fail_count': fail_count
        }, f'成功删除{success_count}条记录')
    
    @app.route('/api/history/update-status/<int:record_id>', methods=['PUT'])
    def update_record_status(record_id):
        """
        更新记录的防治状态
        """
        data = request.get_json()

        if not data:
            return error('请求体不能为空', 400)

        user_id = data.get('user_id')
        status = data.get('status')

        if user_id is None:
            return error('缺少用户ID', 400)

        if not status:
            return error('缺少状态值', 400)

        if status not in ('已防治', '待防治'):
            return error('状态值无效，只能是"已防治"或"待防治"', 400)

        service = get_history_service()
        success_flag, message = service.update_status(record_id, user_id, status)

        if success_flag:
            return success(None, message)
        else:
            return error(message, 400)

    @app.route('/api/history/region-stats', methods=['GET'])
    def get_region_stats():
        """
        获取各地区病害统计数据
        """
        region = request.args.get('region')
        
        try:
            records = DetectionRecord.query.all()
            
            region_stats = {}
            for record in records:
                try:
                    if not record.weather_info or record.weather_info == '':
                        continue
                    
                    weather_info = json.loads(record.weather_info)
                    city = weather_info.get('city')
                    
                    if not city:
                        continue
                    
                    if region and region not in city:
                        continue
                    
                    if city not in region_stats:
                        region_stats[city] = {
                            'city': city,
                            'total_count': 0,
                            'diseases': {}
                        }
                    
                    region_stats[city]['total_count'] += 1
                    
                    disease = record.disease_name
                    if disease not in region_stats[city]['diseases']:
                        region_stats[city]['diseases'][disease] = 0
                    region_stats[city]['diseases'][disease] += 1
                    
                except Exception as e:
                    print(f"处理记录 {record.id} 时出错: {e}")
                    continue
            
            result = []
            for city, stats in region_stats.items():
                top_diseases = sorted(stats['diseases'].items(), key=lambda x: x[1], reverse=True)[:3]
                
                result.append({
                    'city': city,
                    'total_count': stats['total_count'],
                    'top_diseases': [{'name': d[0], 'count': d[1]} for d in top_diseases],
                    'risk_level': _calculate_risk_level(stats['total_count'])
                })
            
            result.sort(key=lambda x: x['total_count'], reverse=True)
            
            return success(result)
            
        except Exception as e:
            print(f"地区统计出错: {e}")
            return success([])


def _calculate_risk_level(total_count):
    """
    根据统计数计算风险等级
    """
    if total_count == 0:
        return '暂无记录'
    elif total_count >= 20:
        return '高风险'
    elif total_count >= 10:
        return '中风险'
    elif total_count >= 1:
        return '低风险'
    return '暂无记录'
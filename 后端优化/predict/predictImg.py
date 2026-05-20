# -*- coding: utf-8 -*-
# @Time : 2024-12-26 12:10
# @Author : 林枫
# @File : predictImg.py
import os
import time
import base64
import io
import cv2
from ultralytics import YOLO
from PIL import Image
import numpy as np

class ImagePredictor:
    """
    病虫害识别预测器
    支持 .pt 或 .onnx 模型（通过 Ultralytics YOLO 统一加载）
    """
    def __init__(self, weights_path, kind, conf=0.5):
        """
        初始化预测器
        :param weights_path: 模型文件路径（.pt 或 .onnx）
        :param kind: 作物类型 ('rice', 'corn', 'strawberry', 'tomato')
        :param conf: 置信度阈值
        """
        print(f"[INFO] 正在加载模型：{weights_path} ...")
        os.environ['CUDA_VISIBLE_DEVICES'] = '0'
        self.model = YOLO(weights_path)
# 方法1：执行一次推理后，再查看设备（不推荐）
# 方法2：直接查看模型加载时使用的提供者（针对 ONNX）

# 如果 weights_path 是 .onnx，可以获取底层的 ONNX Runtime 会话
        if weights_path.endswith('.onnx'):
            try:
                # 获取 session 的提供者信息
                session = self.model.predictor.session
                print(f"ONNX Runtime 提供者: {session.get_providers()}")
                if 'CUDAExecutionProvider' in session.get_providers():
                    print("✅ GPU 已启用 (CUDA)")
                else:
                    print("⚠️ 使用 CPU 推理")
            except:
                print("无法获取设备信息")
        else:
            # .pt 模型可以直接看 device
            print(f"当前推理设备: {self.model.device}")       # Ultralytics 统一接口
        self.conf = conf
        self.kind = kind

        # 标签映射（与训练类别顺序一致）
        self.labels_map = {
            'rice': ['Brown_Spot（褐斑病）', 'Rice_Blast（稻瘟病）', 'Bacterial_Blight（细菌性叶枯病）'],
            'corn': ['blight（疫病）', 'common_rust（普通锈病）', 'gray_spot（灰斑病）', 'health（健康）'],
            'strawberry': ['Angular Leafspot（角斑病）', 'Anthracnose Fruit Rot（炭疽果腐病）',
                           'Blossom Blight（花枯病）', 'Gray Mold（灰霉病）', 'Leaf Spot（叶斑病）',
                           'Powdery Mildew Fruit（白粉病果）', 'Powdery Mildew Leaf（白粉病叶）'],
            'tomato': ['Early Blight（早疫病）', 'Healthy（健康）', 'Late Blight（晚疫病）',
                       'Leaf Miner（潜叶病）', 'Leaf Mold（叶霉病）', 'Mosaic Virus（花叶病毒）',
                       'Septoria（壳针孢属）', 'Spider Mites（蜘蛛螨）', 'Yellow Leaf Curl Virus（黄化卷叶病毒）']
        }
        if kind not in self.labels_map:
            raise ValueError(f"不支持的作物类型：{kind}，可选：{list(self.labels_map.keys())}")
        print(f"[INFO] 模型加载完成，支持标签数：{len(self.labels_map[kind])}")

    def predict(self, image_source):
        """
        执行推理
        :param image_source: 图片路径（字符串）
        :return: dict 包含 success, detections, labels, confidences, image_base64, annotated_path, allTime 等
        """
        start_time = time.time()
        annotated_save_path = None

        try:
            # Ultralytics 推理（自动包含预处理、后处理、NMS）
            results = self.model(image_source, conf=self.conf, verbose=False)
            result = results[0]      # 第一张图片的结果

            # 提取检测信息
            detections = []
            if result.boxes is not None:
                for box in result.boxes:
                    x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
                    conf = float(box.conf[0])
                    cls_id = int(box.cls[0])
                    label = self.labels_map[self.kind][cls_id] if cls_id < len(self.labels_map[self.kind]) else '未知'
                    detections.append({
                        'label': label,
                        'confidence': round(conf, 4),
                        'confidence_str': f"{conf*100:.2f}%",
                        'box': [x1, y1, x2, y2]
                    })

            # 生成标注图（使用 Ultralytics 的 plot 方法）
            annotated_img = result.plot()   # BGR 格式 numpy 数组

            # 保存标注图到本地
            if isinstance(image_source, str):
                annotated_save_path = self._generate_annotated_path(image_source)
                if annotated_save_path:
                    cv2.imwrite(annotated_save_path, annotated_img)
                    print(f"📸 标注图已保存: {annotated_save_path}")

            # 转换为 Base64 供前端直接显示
            annotated_img_rgb = cv2.cvtColor(annotated_img, cv2.COLOR_BGR2RGB)
            pil_img = Image.fromarray(annotated_img_rgb)
            img_base64 = self._pil_to_base64(pil_img)

            elapsed = time.time() - start_time
            all_results = {
                'success': True,
                'detections': detections,
                'labels': [d['label'] for d in detections] if detections else ['无病害'],
                'confidences': [d['confidence_str'] for d in detections] if detections else ['0.00%'],
                'image_base64': img_base64,
                'annotated_path': annotated_save_path,
                'allTime': f"{elapsed:.3f}秒"
            }
            return all_results

        except Exception as e:
            print(f"[ERROR] 预测失败: {e}")
            import traceback
            traceback.print_exc()
            return {
                'success': False,
                'error_msg': str(e),
                'labels': ['预测失败'],
                'confidences': ['0.00%'],
                'allTime': "0.000秒",
                'image_base64': "",
                'annotated_path': None
            }

    # ---------- 辅助方法（与原有接口保持一致）----------
    def _generate_annotated_path(self, original_path):
        """根据原始图片路径生成标注图保存路径"""
        if not isinstance(original_path, str):
            return None
        # 将 uploads 替换为 annotated（兼容正反斜杠）
        import re
        annotated_path = re.sub(r'[/\\]uploads[/\\]', lambda m: m.group(0).replace('uploads', 'annotated'), original_path)
        base, ext = os.path.splitext(annotated_path)
        annotated_path = f"{base}_annotated{ext}"
        os.makedirs(os.path.dirname(annotated_path), exist_ok=True)
        return annotated_path

    def _pil_to_base64(self, pil_image, format="JPEG"):
        """PIL 图像转 Base64 字符串"""
        buffered = io.BytesIO()
        pil_image.save(buffered, format=format)
        img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
        return f"data:image/{format.lower()};base64,{img_str}"

# 测试代码（可选）
if __name__ == '__main__':
    try:
        predictor = ImagePredictor(
            weights_path="weights/rice.onnx",   # 可改为 .pt 文件
            kind='rice',
            conf=0.25
        )
        test_img = r"D:\test.jpg"   # 替换为实际图片路径
        print(f"开始预测图片：{test_img}")
        result = predictor.predict(test_img)
        if result['success']:
            print(f"耗时：{result['allTime']}")
            print(f"检测到 {len(result['detections'])} 个目标")
            for d in result['detections']:
                print(f"  {d['label']} {d['confidence_str']} 位置 {d['box']}")
        else:
            print(f"预测失败：{result.get('error_msg')}")
    except Exception as e:
        print(f"运行出错：{e}")
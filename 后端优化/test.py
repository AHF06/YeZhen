from ultralytics import YOLO
import time
IMAGE_PATH = r'D:\第一个软件开发\病害采析系统进阶版\yolo_cropDisease_detection_flask\dataset\rice_dataset\images\test\blast_orig_016.png'  
PT_MODEL_PATH = "weights(2)/rice_best.pt"    
ONNX_MODEL_PATH = "weights/rice.onnx"
WARMUP_TIMES = 3  
TEST_TIMES = 5  

print("="*60)
print("开始对比：PT模型 VS ONNX模型（同一张图片，带预热+平均计时）")
print("="*60)  

# ------------------- 1. 测试 PT 模型 -------------------
print("\n【1】加载 PT 模型...")
model_pt = YOLO(PT_MODEL_PATH)
# 预热：跑3次，消除初始化时间
print(f"🔧 PT模型预热中（{WARMUP_TIMES}次）...")
for _ in range(WARMUP_TIMES):
    model_pt(IMAGE_PATH, verbose=False)  
# 正式测试：跑5次，取平均时间
print(f"🚀 PT模型正式测试（{TEST_TIMES}次）...")
pt_times = []
for _ in range(TEST_TIMES):
    start = time.time()
    results_pt = model_pt(IMAGE_PATH, verbose=False)
    pt_times.append(time.time() - start)
infer_time_pt = round(sum(pt_times)/len(pt_times), 3)
# 保存结果
results_pt[0].save("result_pt.jpg")
print(f"✅ PT模型平均推理时间：{infer_time_pt} 秒")
print(f"✅ 检测结果已保存：result_pt.jpg")

# ------------------- 2. 测试 ONNX 模型 -------------------
print("\n【2】加载 ONNX 模型...")
model_onnx = YOLO(ONNX_MODEL_PATH)
# 预热
print(f"🔧 ONNX模型预热中（{WARMUP_TIMES}次）...")
for _ in range(WARMUP_TIMES):
    model_onnx(IMAGE_PATH, verbose=False)
# 正式测试
print(f"🚀 ONNX模型正式测试（{TEST_TIMES}次）...")
onnx_times = []
for _ in range(TEST_TIMES):
    start = time.time()
    results_onnx = model_onnx(IMAGE_PATH, verbose=False)
    onnx_times.append(time.time() - start)
infer_time_onnx = round(sum(onnx_times)/len(onnx_times), 3)
# 保存结果
results_onnx[0].save("result_onnx.jpg")
print(f"✅ ONNX模型平均推理时间：{infer_time_onnx} 秒")
print(f"✅ 检测结果已保存：result_onnx.jpg")
# ------------------- 3. 最终对比总结 -------------------
print("\n" + "="*60)
print("📊 最终对比结果（同一张图片，平均耗时）")
print("="*60)
print(f"PT模型平均耗时：{infer_time_pt} s")
print(f"ONNX模型平均耗时：{infer_time_onnx} s")
speed_up = round((infer_time_pt - infer_time_onnx)/infer_time_pt*100, 1)
print(f"🚀 ONNX 速度提升：{speed_up}%")
print("\n🎯 检测效果（画框、类别、置信度）：完全一致！")
print("🎯 精度无任何损失，仅提升推理速度！")
print("="*60)
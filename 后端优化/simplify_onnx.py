import os
import onnx
from onnxsim import simplify

# 你的模型存放目录（请根据实际路径修改）
model_dir = "weights(2)"   # 如果路径有空格或中文，最好用绝对路径或改名
output_dir = "weights_simplified"   # 存放精简后的模型

os.makedirs(output_dir, exist_ok=True)

# 四类作物的文件名（按你实际的 .onnx 文件名）
models = [
    "rice.onnx",
    "corn.onnx",
    "tomato.onnx",
    "strawberry.onnx"
]

for model_name in models:
    input_path = os.path.join(model_dir, model_name)
    if not os.path.exists(input_path):
        print(f"❌ 文件不存在：{input_path}")
        continue

    print(f"正在精简 {model_name} ...")
    # 加载模型
    model = onnx.load(input_path)
    # 简化
    model_simp, check = simplify(model)
    if not check:
        print(f"⚠️ {model_name} 简化验证失败，跳过")
        continue

    output_path = os.path.join(output_dir, model_name.replace(".onnx", "_sim.onnx"))
    onnx.save(model_simp, output_path)
    print(f"✅ 已保存：{output_path}")
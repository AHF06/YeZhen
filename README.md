农作物叶片病虫害检测系统 - 叶诊
基于 YOLOv8 + Ollama 的智能农业病害识别小程序

项目简介
本系统是一款面向种植户、农技人员的微信小程序，通过拍照识别农作物叶片病虫害，结合天气信息生成 AI 防治建议，并提供农友圈交流、历史记录管理、病虫害预警、AI 智能问答等功能。

支持的作物： 水稻、玉米、番茄、草莓

技术栈
前端	uni-app + Vue3 + 微信小程序
后端	Python Flask + SQLAlchemy
数据库	MySQL
深度学习	YOLOv8 + ONNX Runtime
大模型	Ollama + qwen2.5
第三方API	高德地图（天气/定位）

项目结构
crop_disease_backend/
├── 后端优化/                 # Flask 后端
│   ├── app/                  # 应用主目录
│   ├── weights/              # 模型权重文件
│   ├── static/               # 图片存储
│   ├── run.py                # 启动入口
│   └── requirements.txt      # Python 依赖
├── 前端/                     # uni-app 前端
│   ├── pages/                # 页面文件
│   ├── utils/                # 工具函数
│   └── manifest.json         # 小程序配置
└── crop_detect_db.sql        # 数据库脚本

环境要求
Python 3.10+

MySQL 5.7+

微信开发者工具

HBuilderX（可选）

后端部署
# 进入后端目录
cd 后端优化

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 配置数据库
mysql -u root -p < crop_detect_db.sql

# 配置环境变量
cp .env.example .env
# 编辑 .env 填写数据库密码和高德Key

# 安装 Ollama 并拉取模型
ollama pull qwen2.5

# 启动后端
python run.py


前端运行
1、用 HBuilderX 打开 前端/ 文件夹

2、修改 utils/config.js 中的 baseUrl 为后端地址

3、运行 → 运行到小程序模拟器 → 微信开发者工具

4、勾选「不校验合法域名」

核心功能
病虫害识别	（拍照/上传图片，YOLO 模型实时识别）
AI 防治建议	（结合天气信息，生成针对性防治方案）
历史记录	（识别记录管理、搜索、统计报告）
农友圈	（发帖、点赞、评论，农技互助）
预警系统	（天气预警 + 区域预警）
AI 咨询	（多轮农业问答，支持语音输入）

开发团队
安慧芳、姜梦茹、吴美霖、李兰芳、易春涵

许可证
仅供学习交流使用

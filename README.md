# 小红书舆情分析工具

基于豆包 AI 多模态能力的小红书舆情分析工具。上传小红书截图，智能识别内容并生成专业舆情分析报告。

## 功能特点

- 📤 **图片上传** - 支持拖拽或点击上传小红书截图
- 🤖 **智能识别** - AI 识别截图中的笔记封面文字
- 📊 **情感分析** - 分析每条内容的情感倾向
- 🔍 **关键词提取** - 提取热门关键词和主题
- ⚠️ **风险预警** - 识别负面舆情风险
- 📝 **报告生成** - 生成包含洞察和建议的专业报告

## 技术栈

- **后端**: FastAPI + Python 3.9+
- **前端**: 纯 HTML/CSS/JavaScript
- **AI**: 豆包 (Doubao) API - doubao-seed-1-8 模型

## 快速开始

### 1. 配置环境

```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. 配置 API Key

复制 `.env.example` 为 `.env` 并填入你的豆包 API Key：

```bash
cp .env.example .env
# 编辑 .env 文件，填入 DOUBAO_API_KEY
```

### 3. 启动后端

```bash
cd backend
source venv/bin/activate
uvicorn main:app --reload --port 8000
```

### 4. 启动前端

```bash
# 在项目根目录
python3 -m http.server 5173
```

### 5. 访问应用

打开浏览器访问：http://localhost:5173/index.html

## 使用说明

1. 在小红书 App 中搜索关键词，截取搜索结果页面
2. 在工具中上传截图
3. （可选）输入搜索关键词
4. 点击"开始分析"按钮
5. 等待 AI 分析完成，查看舆情报告

## 项目结构

```
.
├── index.html              # 前端页面
├── README.md               # 项目说明
├── backend/                # 后端服务
│   ├── main.py            # FastAPI 入口
│   ├── .env.example       # 环境变量示例
│   ├── requirements.txt   # Python 依赖
│   ├── api/               # API 路由
│   ├── services/          # 业务服务
│   └── schema/            # 数据模型
└── frontend/              # React 前端（备用）
```

## 许可证

MIT License

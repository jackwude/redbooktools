"""
小红书舆情分析工具 - 后端服务
FastAPI 应用入口
"""
import os
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# 检查豆包 API Key 配置
api_key = os.getenv("DOUBAO_API_KEY")
if api_key:
    logger.info("豆包 API 已配置")
else:
    logger.warning("未找到 DOUBAO_API_KEY 环境变量")

# 创建 FastAPI 应用
app = FastAPI(
    title="小红书舆情分析工具",
    description="上传小红书截图，自动识别内容并生成舆情分析报告（基于豆包 AI）",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 开发环境允许所有来源
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
from api.routes import router as api_router
app.include_router(api_router)


@app.get("/")
async def root():
    """
    根路径 - 服务信息
    """
    return {
        "name": "小红书舆情分析工具",
        "version": "1.0.0",
        "ai_provider": "豆包 (Doubao)",
        "docs": "/docs",
        "api": "/api"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )

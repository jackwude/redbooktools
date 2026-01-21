"""
API 路由定义
"""
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import StreamingResponse
from typing import Optional
import logging

from schema.response import AnalyzeResponse, ErrorResponse, AnalysisReport
from services.image_analyzer import get_image_analyzer
from services.sentiment_analyzer import get_sentiment_analyzer
from services.report_generator import get_report_generator
from services.excel_exporter import get_excel_exporter

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["analysis"])


@router.post(
    "/analyze",
    response_model=AnalyzeResponse,
    responses={
        400: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    }
)
async def analyze_screenshot(
    images: list[UploadFile] = File(..., description="小红书搜索结果截图（最多10张）"),
    search_keyword: Optional[str] = Form(
        default=None, 
        description="搜索关键词（可选）"
    )
):
    """
    分析小红书截图并生成舆情报告
    
    - **images**: 小红书搜索结果页面的截图文件列表（PNG/JPG），最多10张
    - **search_keyword**: 可选的搜索关键词，用于辅助分析
    
    返回完整的舆情分析报告，包括：
    - 帖子识别结果
    - 情感分析
    - 关键词提取
    - 风险预警
    - 分析洞察和建议
    """
    # 验证图片数量
    if len(images) > 10:
        raise HTTPException(
            status_code=400,
            detail="最多只能上传 10 张图片"
        )
    
    if len(images) == 0:
        raise HTTPException(
            status_code=400,
            detail="请至少上传 1 张图片"
        )
    
    # 验证文件类型
    for image in images:
        if image.content_type not in ["image/png", "image/jpeg", "image/jpg", "image/webp"]:
            raise HTTPException(
                status_code=400,
                detail=f"文件 {image.filename} 格式不支持，请上传 PNG、JPG 或 WebP 格式的图片"
            )
    
    try:
        all_posts_data = []
        
        # 逐个处理每张图片
        for idx, image in enumerate(images):
            # 读取图片数据
            image_data = await image.read()
            logger.info(f"处理第 {idx+1}/{len(images)} 张图片: {image.filename}, 大小: {len(image_data)} bytes")
            
            # Step 1: 图像识别 - 提取帖子信息
            image_analyzer = get_image_analyzer()
            extraction_result = await image_analyzer.analyze_image(
                image_data, 
                mime_type=image.content_type
            )
            
            posts_data = extraction_result.get("posts", [])
            logger.info(f"从第 {idx+1} 张图片中识别到 {len(posts_data)} 个帖子")
            
            all_posts_data.extend(posts_data)
        
        logger.info(f"共识别到 {len(all_posts_data)} 个帖子")
        
        if not all_posts_data:
            return AnalyzeResponse(
                success=True,
                message="未能从截图中识别到小红书帖子内容",
                data=None
            )
        
        # Step 2: 情感分析（对所有帖子进行统一分析）
        sentiment_analyzer = get_sentiment_analyzer()
        sentiment_result = await sentiment_analyzer.analyze_sentiment(all_posts_data)
        
        # 合并帖子信息和情感分析结果
        analyzed_posts = sentiment_analyzer.merge_post_info(
            all_posts_data,
            sentiment_result.get("analyzed_posts", [])
        )
        
        # Step 3: 生成舆情报告
        report_generator = get_report_generator()
        report = await report_generator.generate_report(
            posts=analyzed_posts,
            keywords_data=sentiment_result.get("top_keywords", []),
            risk_alerts_data=sentiment_result.get("risk_alerts", []),
            search_keyword=search_keyword
        )
        
        return AnalyzeResponse(
            success=True,
            message=f"舆情分析完成，共分析 {len(images)} 张图片，识别到 {len(all_posts_data)} 个帖子",
            data=report
        )
        
    except Exception as e:
        logger.error(f"分析过程发生错误: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"分析过程发生错误: {str(e)}"
        )


@router.get("/health")
async def health_check():
    """
    健康检查接口
    """
    return {"status": "healthy", "service": "sentiment-analysis"}


@router.post("/export/excel")
async def export_to_excel(report: AnalysisReport):
    """
    导出分析报告为 Excel 文件
    
    - **report**: 分析报告数据对象
    
    返回 Excel 文件供下载
    """
    try:
        # 获取 Excel 导出器
        exporter = get_excel_exporter()
        
        # 将报告数据转换为字典
        report_dict = report.model_dump() if hasattr(report, 'model_dump') else report.dict()
        
        # 生成 Excel 文件
        excel_file = await exporter.export_analysis_report(report_dict)
        
        # 生成文件名
        from datetime import datetime
        from urllib.parse import quote
        
        filename = f"小红书舆情分析报告_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        encoded_filename = quote(filename)
        
        # 返回文件流
        return StreamingResponse(
            excel_file,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}",
                "Access-Control-Expose-Headers": "Content-Disposition"
            }
        )
        
    except Exception as e:
        logger.error(f"Excel 导出失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Excel 导出失败: {str(e)}"
        )

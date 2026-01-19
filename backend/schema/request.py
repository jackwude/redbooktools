"""
请求数据模型
"""
from pydantic import BaseModel, Field
from typing import Optional


class AnalyzeRequest(BaseModel):
    """
    舆情分析请求模型
    """
    search_keyword: Optional[str] = Field(
        default=None,
        description="搜索关键词（可选，用于辅助分析）"
    )


class AnalysisStatusRequest(BaseModel):
    """
    分析状态查询请求
    """
    analysis_id: str = Field(description="分析任务 ID")

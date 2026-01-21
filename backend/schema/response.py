"""
响应数据模型
"""
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from enum import Enum


class SentimentType(str, Enum):
    """情感类型枚举"""
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"


class CommentReply(BaseModel):
    """
    评论回复信息
    """
    author: str = Field(description="回复者昵称")
    content: str = Field(description="回复内容")


class CommentInfo(BaseModel):
    """
    评论信息
    """
    author: str = Field(description="评论者昵称")
    content: str = Field(description="评论内容")
    likes: Optional[int] = Field(default=None, description="评论点赞数")
    time: Optional[str] = Field(default=None, description="评论时间")
    is_author_reply: bool = Field(default=False, description="是否为作者回复")
    replies: List[CommentReply] = Field(default_factory=list, description="回复列表")
    post_title: Optional[str] = Field(default=None, description="所属帖子标题")
    screenshot_index: Optional[int] = Field(default=None, description="来源截图序号")


class PostInfo(BaseModel):
    """
    小红书帖子信息
    """
    title: str = Field(description="帖子标题")
    content: str = Field(default="", description="帖子内容摘要")
    author: str = Field(default="", description="作者昵称")
    likes: Optional[int] = Field(default=None, description="点赞数")
    comments: Optional[int] = Field(default=None, description="评论数")
    sentiment: SentimentType = Field(description="情感倾向")
    sentiment_score: float = Field(
        ge=-1.0, le=1.0,
        description="情感得分，-1 到 1 之间"
    )
    keywords: List[str] = Field(default_factory=list, description="关键词列表")



class SentimentDistribution(BaseModel):
    """
    情感分布统计
    """
    positive_count: int = Field(default=0, description="正面帖子数量")
    negative_count: int = Field(default=0, description="负面帖子数量")
    neutral_count: int = Field(default=0, description="中性帖子数量")
    positive_ratio: float = Field(default=0.0, description="正面比例")
    negative_ratio: float = Field(default=0.0, description="负面比例")
    neutral_ratio: float = Field(default=0.0, description="中性比例")


class KeywordInfo(BaseModel):
    """
    关键词信息
    """
    word: str = Field(description="关键词")
    count: int = Field(description="出现次数")
    sentiment: SentimentType = Field(description="主要情感倾向")


class RiskAlert(BaseModel):
    """
    风险预警信息
    """
    level: str = Field(description="风险等级: high/medium/low")
    description: str = Field(description="风险描述")
    related_posts: List[str] = Field(default_factory=list, description="相关帖子标题")


class AnalysisReport(BaseModel):
    """
    舆情分析报告
    """
    analysis_id: str = Field(description="分析任务 ID")
    search_keyword: Optional[str] = Field(default=None, description="搜索关键词")
    total_posts: int = Field(description="识别的帖子总数")
    total_comments: int = Field(default=0, description="识别的评论总数")
    sentiment_distribution: SentimentDistribution = Field(description="情感分布")
    top_keywords: List[KeywordInfo] = Field(description="热门关键词")
    posts: List[PostInfo] = Field(description="帖子详情列表")
    comments: List[CommentInfo] = Field(default_factory=list, description="评论列表")
    risk_alerts: List[RiskAlert] = Field(default_factory=list, description="风险预警")
    summary: str = Field(description="舆情分析总结")
    insights: List[str] = Field(default_factory=list, description="关键洞察")
    recommendations: List[str] = Field(default_factory=list, description="建议措施")
    created_at: str = Field(description="报告生成时间")



class AnalyzeResponse(BaseModel):
    """
    分析接口响应
    """
    success: bool = Field(description="是否成功")
    message: str = Field(description="响应消息")
    data: Optional[AnalysisReport] = Field(default=None, description="分析报告")


class ErrorResponse(BaseModel):
    """
    错误响应
    """
    success: bool = Field(default=False)
    message: str = Field(description="错误消息")
    error_code: str = Field(description="错误代码")

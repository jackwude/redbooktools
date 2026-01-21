"""
报告生成服务
整合分析结果生成舆情分析报告
"""
from __future__ import annotations
import httpx
import json
import logging
import os
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
from schema.response import (
    AnalysisReport,
    PostInfo,
    CommentInfo,
    SentimentDistribution,
    KeywordInfo,
    RiskAlert,
    SentimentType
)

logger = logging.getLogger(__name__)

# 豆包 API 配置
DOUBAO_API_URL = "https://ark.cn-beijing.volces.com/api/v3/responses"
DOUBAO_MODEL = "doubao-seed-1-8-251228"

# 洞察生成提示词
INSIGHTS_PROMPT = """
你是一个专业的舆情分析专家。基于以下舆情分析数据，请生成专业的分析洞察和建议。

分析数据：
- 总帖子数: {total_posts}
- 正面帖子比例: {positive_ratio:.1%}
- 负面帖子比例: {negative_ratio:.1%}
- 中性帖子比例: {neutral_ratio:.1%}
- 热门关键词: {top_keywords}
- 风险预警数量: {risk_count}

帖子详情摘要：
{posts_summary}

请生成：
1. 3-5 条关键洞察（每条 20-50 字）
2. 3-5 条建议措施（每条 20-50 字）
3. 一段 100-200 字的舆情分析总结

请以 JSON 格式返回：
{{
    "insights": ["洞察1", "洞察2", ...],
    "recommendations": ["建议1", "建议2", ...],
    "summary": "舆情分析总结..."
}}

请只返回 JSON 格式的结果，不要有其他文字。
"""


class ReportGenerator:
    """
    报告生成器
    整合所有分析结果生成最终的舆情报告
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        初始化报告生成器
        
        Args:
            api_key: 豆包 API Key
        """
        self.api_key = api_key or os.getenv("DOUBAO_API_KEY")
        if not self.api_key:
            raise ValueError("未配置 DOUBAO_API_KEY")
    
    async def _call_doubao_api(self, prompt: str) -> str:
        """
        调用豆包 API
        """
        payload = {
            "model": DOUBAO_MODEL,
            "input": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_text",
                            "text": prompt
                        }
                    ]
                }
            ]
        }
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        async with httpx.AsyncClient(timeout=180.0) as client:
            response = await client.post(
                DOUBAO_API_URL,
                json=payload,
                headers=headers
            )
            response.raise_for_status()
            result = response.json()
        
        # 解析响应 - output 是数组格式
        response_text = ""
        if "output" in result:
            output = result["output"]
            if isinstance(output, list):
                for item in output:
                    if isinstance(item, dict) and item.get("type") == "message":
                        content = item.get("content", [])
                        if isinstance(content, list):
                            for c in content:
                                if isinstance(c, dict) and c.get("type") == "output_text":
                                    response_text = c.get("text", "")
                                    break
                        elif isinstance(content, str):
                            response_text = content
                        break
            elif isinstance(output, dict) and "content" in output:
                response_text = output["content"]
            elif isinstance(output, str):
                response_text = output
        elif "choices" in result:
            choices = result["choices"]
            if choices and len(choices) > 0:
                message = choices[0].get("message", {})
                response_text = message.get("content", "")
        
        return response_text
    
    def calculate_sentiment_distribution(
        self, 
        posts: List[PostInfo]
    ) -> SentimentDistribution:
        """
        计算情感分布统计
        
        Args:
            posts: 帖子信息列表
            
        Returns:
            情感分布统计对象
        """
        total = len(posts)
        if total == 0:
            return SentimentDistribution()
        
        positive_count = sum(1 for p in posts if p.sentiment == SentimentType.POSITIVE)
        negative_count = sum(1 for p in posts if p.sentiment == SentimentType.NEGATIVE)
        neutral_count = sum(1 for p in posts if p.sentiment == SentimentType.NEUTRAL)
        
        return SentimentDistribution(
            positive_count=positive_count,
            negative_count=negative_count,
            neutral_count=neutral_count,
            positive_ratio=positive_count / total,
            negative_ratio=negative_count / total,
            neutral_ratio=neutral_count / total
        )
    
    def parse_keywords(self, keywords_data: List[Dict[str, Any]]) -> List[KeywordInfo]:
        """
        解析关键词数据
        
        Args:
            keywords_data: 原始关键词数据
            
        Returns:
            KeywordInfo 列表
        """
        result = []
        for kw in keywords_data[:10]:  # 最多取前 10 个
            try:
                sentiment_str = kw.get("sentiment", "neutral")
                try:
                    sentiment = SentimentType(sentiment_str)
                except ValueError:
                    sentiment = SentimentType.NEUTRAL
                
                result.append(KeywordInfo(
                    word=kw.get("word", ""),
                    count=kw.get("count", 1),
                    sentiment=sentiment
                ))
            except Exception as e:
                logger.warning(f"解析关键词失败: {e}")
                continue
        
        return result
    
    def parse_risk_alerts(self, alerts_data: List[Dict[str, Any]]) -> List[RiskAlert]:
        """
        解析风险预警数据
        
        Args:
            alerts_data: 原始风险预警数据
            
        Returns:
            RiskAlert 列表
        """
        result = []
        for alert in alerts_data:
            try:
                result.append(RiskAlert(
                    level=alert.get("level", "low"),
                    description=alert.get("description", ""),
                    related_posts=alert.get("related_posts", [])
                ))
            except Exception as e:
                logger.warning(f"解析风险预警失败: {e}")
                continue
        
        return result
    
    async def generate_insights(
        self,
        posts: List[PostInfo],
        sentiment_dist: SentimentDistribution,
        keywords: List[KeywordInfo],
        risk_alerts: List[RiskAlert]
    ) -> Dict[str, Any]:
        """
        生成分析洞察和建议
        
        Args:
            posts: 帖子列表
            sentiment_dist: 情感分布
            keywords: 关键词列表
            risk_alerts: 风险预警列表
            
        Returns:
            包含洞察、建议和总结的字典
        """
        try:
            # 准备帖子摘要
            posts_summary = "\n".join([
                f"- [{p.sentiment.value}] {p.title[:50]}..." 
                for p in posts[:10]  # 最多展示 10 条
            ])
            
            # 准备关键词列表
            top_keywords = ", ".join([kw.word for kw in keywords[:5]])
            
            prompt = INSIGHTS_PROMPT.format(
                total_posts=len(posts),
                positive_ratio=sentiment_dist.positive_ratio,
                negative_ratio=sentiment_dist.negative_ratio,
                neutral_ratio=sentiment_dist.neutral_ratio,
                top_keywords=top_keywords,
                risk_count=len(risk_alerts),
                posts_summary=posts_summary
            )
            
            response_text = await self._call_doubao_api(prompt)
            response_text = response_text.strip()
            
            # 移除可能存在的 markdown 代码块标记
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.startswith("```"):
                response_text = response_text[3:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            
            return json.loads(response_text.strip())
            
        except Exception as e:
            logger.error(f"生成洞察失败: {e}")
            return {
                "insights": ["数据分析完成，请查看详细报告"],
                "recommendations": ["建议持续监测舆情变化"],
                "summary": "舆情分析已完成，共识别相关帖子若干条。"
            }
    
    async def generate_report(
        self,
        posts: List[PostInfo],
        keywords_data: List[Dict[str, Any]],
        risk_alerts_data: List[Dict[str, Any]],
        comments_data: Optional[List[Dict[str, Any]]] = None,
        search_keyword: Optional[str] = None
    ) -> AnalysisReport:
        """
        生成完整的舆情分析报告
        
        Args:
            posts: 帖子信息列表
            keywords_data: 关键词原始数据
            risk_alerts_data: 风险预警原始数据
            comments_data: 评论原始数据（可选）
            search_keyword: 搜索关键词
            
        Returns:
            完整的分析报告
        """
        # 生成分析 ID
        analysis_id = str(uuid.uuid4())[:8]
        
        # 计算情感分布
        sentiment_dist = self.calculate_sentiment_distribution(posts)
        
        # 解析关键词和风险预警
        keywords = self.parse_keywords(keywords_data)
        risk_alerts = self.parse_risk_alerts(risk_alerts_data)
        
        # 解析评论数据
        comments = []
        if comments_data:
            for comment_dict in comments_data:
                try:
                    # 处理回复数据
                    replies_data = comment_dict.get("replies", [])
                    from schema.response import CommentReply
                    replies = [
                        CommentReply(
                            author=reply.get("author", ""),
                            content=reply.get("content", "")
                        )
                        for reply in replies_data
                    ]
                    
                    comments.append(CommentInfo(
                        author=comment_dict.get("author", ""),
                        content=comment_dict.get("content", ""),
                        likes=comment_dict.get("likes"),
                        time=comment_dict.get("time"),
                        is_author_reply=comment_dict.get("is_author_reply", False),
                        replies=replies,
                        post_title=comment_dict.get("post_title"),
                        screenshot_index=comment_dict.get("screenshot_index")
                    ))
                except Exception as e:
                    logger.warning(f"解析评论数据失败: {e}")
                    continue
        
        # 生成洞察和建议
        insights_data = await self.generate_insights(
            posts, sentiment_dist, keywords, risk_alerts
        )
        
        # 构建报告
        report = AnalysisReport(
            analysis_id=analysis_id,
            search_keyword=search_keyword,
            total_posts=len(posts),
            total_comments=len(comments),
            sentiment_distribution=sentiment_dist,
            top_keywords=keywords,
            posts=posts,
            comments=comments,
            risk_alerts=risk_alerts,
            summary=insights_data.get("summary", ""),
            insights=insights_data.get("insights", []),
            recommendations=insights_data.get("recommendations", []),
            created_at=datetime.now().isoformat()
        )
        
        logger.info(f"报告生成完成，ID: {analysis_id}，包含 {len(posts)} 个帖子和 {len(comments)} 条评论")
        return report



# 全局生成器实例
_generator: Optional[ReportGenerator] = None


def get_report_generator(api_key: Optional[str] = None) -> ReportGenerator:
    """
    获取报告生成器实例（单例模式）
    """
    global _generator
    if _generator is None:
        _generator = ReportGenerator(api_key)
    return _generator

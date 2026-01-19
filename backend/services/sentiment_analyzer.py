"""
情感分析服务
使用豆包 (Doubao) API 对帖子内容进行情感分析和关键词提取
"""
from __future__ import annotations
import httpx
import json
import logging
import os
from typing import List, Dict, Any, Optional
from schema.response import SentimentType, PostInfo, KeywordInfo

logger = logging.getLogger(__name__)

# 豆包 API 配置
DOUBAO_API_URL = "https://ark.cn-beijing.volces.com/api/v3/responses"
DOUBAO_MODEL = "doubao-seed-1-8-251228"

# 情感分析提示词
SENTIMENT_PROMPT = """
你是一个专业的舆情分析师。请对以下小红书帖子进行深度分析，包括情感分析和关键词提取。

帖子列表：
{posts_json}

请对每个帖子进行以下分析：
1. 情感倾向（positive/negative/neutral）
2. 情感得分（-1 到 1 之间的浮点数，-1 表示极度负面，1 表示极度正面）
3. 提取 3-5 个关键词

同时，请汇总所有帖子，提取：
1. 整体热门关键词（按出现频率排序，取前 10 个）
2. 每个关键词的主要情感倾向
3. 潜在的风险点和负面舆情

请以 JSON 格式返回结果：
{{
    "analyzed_posts": [
        {{
            "original_title": "原始标题",
            "sentiment": "positive/negative/neutral",
            "sentiment_score": 0.8,
            "keywords": ["关键词1", "关键词2"]
        }}
    ],
    "top_keywords": [
        {{
            "word": "关键词",
            "count": 5,
            "sentiment": "positive/negative/neutral"
        }}
    ],
    "risk_alerts": [
        {{
            "level": "high/medium/low",
            "description": "风险描述",
            "related_posts": ["相关帖子标题"]
        }}
    ],
    "overall_sentiment": "positive/negative/neutral",
    "sentiment_summary": "整体情感分析总结"
}}

请只返回 JSON 格式的结果，不要有其他文字。
"""


class SentimentAnalyzer:
    """
    情感分析器
    对帖子内容进行情感分析和关键词提取
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        初始化情感分析器
        
        Args:
            api_key: 豆包 API Key
        """
        self.api_key = api_key or os.getenv("DOUBAO_API_KEY")
        if not self.api_key:
            raise ValueError("未配置 DOUBAO_API_KEY")
    
    async def _call_doubao_api(self, prompt: str) -> str:
        """
        调用豆包 API
        
        Args:
            prompt: 提示词
            
        Returns:
            API 响应文本
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
    
    async def analyze_sentiment(self, posts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        对帖子列表进行情感分析
        
        Args:
            posts: 帖子信息列表（来自图像识别结果）
            
        Returns:
            包含情感分析结果的字典
        """
        if not posts:
            return {
                "analyzed_posts": [],
                "top_keywords": [],
                "risk_alerts": [],
                "overall_sentiment": "neutral",
                "sentiment_summary": "没有可分析的帖子内容"
            }
        
        try:
            # 构建提示词
            posts_json = json.dumps(posts, ensure_ascii=False, indent=2)
            prompt = SENTIMENT_PROMPT.format(posts_json=posts_json)
            
            # 调用豆包 API
            response_text = await self._call_doubao_api(prompt)
            response_text = response_text.strip()
            
            # 移除可能存在的 markdown 代码块标记
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.startswith("```"):
                response_text = response_text[3:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            
            result = json.loads(response_text.strip())
            
            logger.info(f"情感分析完成，整体情感倾向: {result.get('overall_sentiment')}")
            return result
            
        except json.JSONDecodeError as e:
            logger.error(f"解析情感分析响应失败: {e}")
            return {
                "analyzed_posts": [],
                "top_keywords": [],
                "risk_alerts": [],
                "overall_sentiment": "neutral",
                "sentiment_summary": "分析过程中发生错误",
                "error": str(e)
            }
        except Exception as e:
            logger.error(f"情感分析失败: {e}")
            raise
    
    def merge_post_info(
        self, 
        original_posts: List[Dict[str, Any]], 
        analyzed_posts: List[Dict[str, Any]]
    ) -> List[PostInfo]:
        """
        合并原始帖子信息和情感分析结果
        
        Args:
            original_posts: 图像识别得到的原始帖子列表
            analyzed_posts: 情感分析得到的结果列表
            
        Returns:
            合并后的 PostInfo 列表
        """
        result = []
        
        # 创建标题到分析结果的映射
        analysis_map = {
            post.get("original_title", ""): post 
            for post in analyzed_posts
        }
        
        for original in original_posts:
            title = original.get("title", "")
            analysis = analysis_map.get(title, {})
            
            # 确定情感类型
            sentiment_str = analysis.get("sentiment", "neutral")
            try:
                sentiment = SentimentType(sentiment_str)
            except ValueError:
                sentiment = SentimentType.NEUTRAL
            
            post_info = PostInfo(
                title=title or "",
                content=original.get("content") or "",
                author=original.get("author") or "",
                likes=original.get("likes"),
                comments=original.get("comments"),
                sentiment=sentiment,
                sentiment_score=analysis.get("sentiment_score", 0.0) or 0.0,
                keywords=analysis.get("keywords") or []
            )
            result.append(post_info)
        
        return result


# 全局分析器实例
_analyzer: Optional[SentimentAnalyzer] = None


def get_sentiment_analyzer(api_key: Optional[str] = None) -> SentimentAnalyzer:
    """
    获取情感分析器实例（单例模式）
    """
    global _analyzer
    if _analyzer is None:
        _analyzer = SentimentAnalyzer(api_key)
    return _analyzer

"""
图像分析服务
使用豆包 (Doubao) API 多模态能力识别小红书截图中的帖子内容
"""
from __future__ import annotations
import httpx
import base64
import json
import logging
import os
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

# 豆包 API 配置
DOUBAO_API_URL = "https://ark.cn-beijing.volces.com/api/v3/responses"
DOUBAO_MODEL = "doubao-seed-1-8-251228"

# 用于提取小红书截图中文字信息的提示词
EXTRACTION_PROMPT = """
你是一个专业的图像文字识别助手。请仔细分析这张小红书截图，识别并提取其中所有可见的文字内容。

请识别以下内容：
1. 每个笔记封面上显示的标题文字
2. 作者昵称（如果可见）
3. 点赞数或互动数据（如果可见）

请将每一条识别到的内容作为一个独立的帖子记录。

请以 JSON 格式返回结果，格式如下：
{
    "posts": [
        {
            "title": "封面上的标题文字",
            "author": "作者昵称（如无则为空）",
            "content": "",
            "likes": null,
            "comments": null
        }
    ],
    "total_visible_posts": 5,
    "notes": "识别说明"
}

重要提示：
- 只要能识别到封面上的任何文字，就算作一条帖子记录
- title 字段填写封面上最显眼的标题文字
- 如果某个字段无法识别，请使用 null 或空字符串
- 数字如果显示为 "1.2万" 这样的格式，请转换为数字 12000
- 务必识别截图中所有可见的笔记封面文字

请只返回 JSON 格式的结果，不要有其他文字。
"""


class ImageAnalyzer:
    """
    图像分析器
    使用豆包 API 识别小红书截图中的帖子内容
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        初始化图像分析器
        
        Args:
            api_key: 豆包 API Key，如果为 None 则从环境变量读取
        """
        self.api_key = api_key or os.getenv("DOUBAO_API_KEY")
        if not self.api_key:
            raise ValueError("未配置 DOUBAO_API_KEY")
    
    async def analyze_image(self, image_data: bytes, mime_type: str = "image/png") -> Dict[str, Any]:
        """
        分析小红书截图，提取帖子信息
        
        Args:
            image_data: 图片的二进制数据
            mime_type: 图片的 MIME 类型
            
        Returns:
            包含提取的帖子信息的字典
        """
        try:
            # 将图片数据编码为 base64 data URL
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            data_url = f"data:{mime_type};base64,{image_base64}"
            
            # 构建豆包 API 请求
            payload = {
                "model": DOUBAO_MODEL,
                "input": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "input_image",
                                "image_url": data_url
                            },
                            {
                                "type": "input_text",
                                "text": EXTRACTION_PROMPT
                            }
                        ]
                    }
                ]
            }
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            # 发送请求（增加超时时间以处理大图片）
            async with httpx.AsyncClient(timeout=180.0) as client:
                logger.info("正在调用豆包 API...")
                response = await client.post(
                    DOUBAO_API_URL,
                    json=payload,
                    headers=headers
                )
                response.raise_for_status()
                result = response.json()
                logger.info(f"豆包 API 响应成功: {list(result.keys())}")
            
            # 解析响应 - 豆包 API 响应格式
            # 实际响应结构: { "output": [ { "type": "message", "content": [ { "type": "output_text", "text": "..." } ] } ] }
            logger.info(f"豆包 API 完整响应: {json.dumps(result, ensure_ascii=False)[:2000]}")
            
            response_text = ""
            if "output" in result:
                output = result["output"]
                logger.info(f"output 字段类型: {type(output)}")
                
                # output 是数组格式
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
                # output 是 dict 格式（旧格式兼容）
                elif isinstance(output, dict) and "content" in output:
                    response_text = output["content"]
                elif isinstance(output, str):
                    response_text = output
            elif "choices" in result:
                # 兼容 OpenAI 格式的响应
                choices = result["choices"]
                if choices and len(choices) > 0:
                    message = choices[0].get("message", {})
                    response_text = message.get("content", "")
            
            if not response_text:
                logger.warning(f"无法解析豆包 API 响应，完整结果: {result}")
                response_text = json.dumps(result)
            
            logger.info(f"AI 原始响应 (前500字符): {response_text[:500]}")
            response_text = response_text.strip()
            
            # 移除可能存在的 markdown 代码块标记
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.startswith("```"):
                response_text = response_text[3:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            
            parsed_result = json.loads(response_text.strip())
            
            logger.info(f"成功识别 {len(parsed_result.get('posts', []))} 个帖子")
            logger.info(f"识别结果: {parsed_result}")
            return parsed_result
            
        except json.JSONDecodeError as e:
            logger.error(f"解析 AI 响应失败: {e}")
            return {
                "posts": [],
                "error": "无法解析 AI 响应",
                "raw_response": response_text if 'response_text' in locals() else None
            }
        except httpx.HTTPStatusError as e:
            logger.error(f"豆包 API 请求失败: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"图像分析失败: {e}")
            raise


# 全局分析器实例（延迟初始化）
_analyzer: Optional[ImageAnalyzer] = None


def get_image_analyzer(api_key: Optional[str] = None) -> ImageAnalyzer:
    """
    获取图像分析器实例（单例模式）
    """
    global _analyzer
    if _analyzer is None:
        _analyzer = ImageAnalyzer(api_key)
    return _analyzer

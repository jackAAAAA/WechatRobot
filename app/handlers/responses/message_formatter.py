"""
消息格式化模块，用于统一处理和格式化不同AI服务提供商返回的消息格式
"""
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class MessageFormatter:
    """消息格式化处理工具类"""
    
    @staticmethod
    def format_ai_response(source: str, provider: str, model: str, content: str, 
                          error: Optional[str] = None) -> str:
        """格式化AI响应消息
        
        Args:
            source: 消息来源 (wechat/wecom等)
            provider: AI服务提供商名称
            model: 使用的模型名称
            content: 响应内容
            error: 错误信息(如果有)
            
        Returns:
            格式化后的消息文本
        """
        if error:
            return f"Error from {provider}/{model}: {error}"
        
        # 根据不同来源和提供商，可以定制不同的格式
        if source == 'wechat':
            # 微信公众号的消息格式
            return f"{provider}/{model}:\n\n{content}"
        elif source == 'wecom':
            # 企业微信的消息格式
            return f"[{provider}/{model}]\n{content}"
        else:
            # 默认格式
            return f"{provider}/{model}: {content}"
    
    @staticmethod
    def split_message(message: str, max_length: int = 2000) -> list:
        """将长消息分割成多个片段
        
        Args:
            message: 完整消息文本
            max_length: 每个片段的最大长度
            
        Returns:
            消息片段列表
        """
        if len(message) <= max_length:
            return [message]
        
        # 按字节长度分割消息
        chunks = []
        current_chunk = ""
        current_size = 0
        
        for char in message:
            char_size = len(char.encode('utf-8'))
            if current_size + char_size > max_length:
                chunks.append(current_chunk)
                current_chunk = ""
                current_size = 0
            
            current_chunk += char
            current_size += char_size
        
        if current_chunk:
            chunks.append(current_chunk)
        
        return chunks 
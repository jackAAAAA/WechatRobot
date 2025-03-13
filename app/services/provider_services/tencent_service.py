import logging
import json
import httpx
from typing import Dict, Any, Optional

from app.services.provider_services.base_service import BaseProviderService
from app.config.config import Config
from app.utils.celery_utils import celery
from openai import OpenAI

logger = logging.getLogger(__name__)

class TencentProvider(BaseProviderService):
    """Service for handling Tencent AI API requests"""
    
    def __init__(self, model: Optional[str] = None):
        """Initialize the Tencent provider service
        
        Args:
            model: The specific model to use, or None to use the default
        """
        super().__init__(model)
        # Set default model if none provided
        if not self.model:
            self.model = Config.TENCENT_MODEL_DEEPSEEK_R1_671B
    
    def process(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Process the request with Tencent
        
        Args:
            params: The request parameters
            
        Returns:
            Dictionary containing the result and metadata
        """
        if 'content' not in params:
            # For non-text messages or other unsupported types
            return {
                'content': 'Sorry, I can only process text messages.',
                'provider': 'Tencent',
                'model': self.model,
                'async': False
            }
        
        # For better response times, process the request asynchronously
        # and return an immediate response
        self._process_request_task.delay(
            user_id=params['from_user'],
            query=params['content'],
            model=self.model,
            source=params['source']
        )
        
        return {
            #'content': 'Your request is being processed...',
            'provider': f'Tencent/{self.model}',
            'model': self.model,
            'async': True
        }
    
    @celery.task(name="tencent_service.process_request")
    def _process_request_task(user_id: str, query: str, model: str, source: str):
        """Celery task to process a request with Tencent
        
        Args:
            user_id: The user ID
            query: The user's query
            model: The model to use
            source: The source of the request (wechat/wecom)
        """
        try:
            # Implement Tencent API client
            # This is a simplified version - you would need to implement
            # the actual API client for Tencent's services

            client = OpenAI(
                api_key=Config.TENCENT_API_KEY,
                base_url=Config.TENCENT_API_BASE
            )

            reasoning_content = ""  # 定义完整思考过程
            answer_content = ""     # 定义完整回复
            is_answering = False   # 判断是否结束思考过程并开始回复
            token_usage = 0 # 定义一次回答的token使用情况

            # 创建聊天完成请求
            stream = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "user", "content": query}
                ],
                temperature=0.7,
                max_tokens=64000,
                stream=True
            )

            reasoning_content += "<think>\n"

            for chunk in stream:
                # 去最后一个chunk来处理usage信息
                if hasattr(chunk, 'usage') and chunk.usage:
                    if hasattr(chunk.usage, 'total_tokens'):
                        token_usage = chunk.usage.total_tokens

                # 如果chunk没有choices，则跳过
                if not getattr(chunk, 'choices', None): 
                    continue

                delta = chunk.choices[0].delta

                # 处理空内容情况：即如果delta没有reasoning_content和content，则跳过
                if not getattr(delta, 'reasoning_content', None) and not getattr(delta, 'content', None): 
                    continue

                # 处理开始回答的情况
                if not getattr(delta, 'reasoning_content', None) and not is_answering:
                    reasoning_content += "</think>"
                    is_answering = True

                # 处理思考过程
                if getattr(delta, 'reasoning_content', None):
                    reasoning_content += delta.reasoning_content
                # 处理回复内容
                elif getattr(delta, 'content', None):
                    answer_content += delta.content
            
            full_content = "Token_usage: " + str(token_usage) + "\n" + reasoning_content + answer_content
            
            # Send the response back to the user
            # Dynamically import the appropriate adapter
            if source == 'wechat':
                from app.adapters.source_adapters.wechat_adapter import WechatAdapter
                adapter = WechatAdapter()
            elif source == 'wecom':
                from app.adapters.source_adapters.wecom_adapter import WecomAdapter
                adapter = WecomAdapter(provider="Tencent", model="DS－R1－671B")
            else:
                logger.error(f"Unknown source: {source}")
                return
            
            # Send the message
            adapter.send_message(user_id, full_content, f"Tencent/{model}")
            logger.info(f"Tencent response sent to user content: {full_content}")
            
        except Exception as e:
            logger.error(f"Error processing Tencent request: {str(e)}")
            # Try to notify the user about the error
            try:
                if source == 'wechat':
                    from app.adapters.source_adapters.wechat_adapter import WechatAdapter
                    adapter = WechatAdapter()
                elif source == 'wecom':
                    from app.adapters.source_adapters.wecom_adapter import WecomAdapter
                    adapter = WecomAdapter(provider="Tencent", model="DS－R1－671B")
                else:
                    return
                
                adapter.send_message(user_id, f"Sorry, there was an error processing your request with Tencent: {str(e)}")
            except:
                logger.error("Failed to send error notification to user") 
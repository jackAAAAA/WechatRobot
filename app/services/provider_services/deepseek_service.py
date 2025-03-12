import logging
import httpx
from typing import Dict, Any, Optional

from app.services.provider_services.base_service import BaseProviderService
from app.config.config import Config
from app.utils.celery_utils import celery

logger = logging.getLogger(__name__)

class DeepseekProvider(BaseProviderService):
    """Service for handling DeepSeek AI API requests"""
    
    def __init__(self, model: Optional[str] = None):
        """Initialize the DeepSeek provider service
        
        Args:
            model: The specific model to use, or None to use the default
        """
        super().__init__(model)
        # Set default model if none provided
        if not self.model:
            self.model = Config.DEEPSEEK_CHAT
    
    def process(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Process the request with DeepSeek
        
        Args:
            params: The request parameters
            
        Returns:
            Dictionary containing the result and metadata
        """
        if 'content' not in params:
            # For non-text messages or other unsupported types
            return {
                'content': 'Sorry, I can only process text messages.',
                'provider': 'DeepSeek',
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
            'content': 'Your request is being processed...',
            'provider': f'DeepSeek/{self.model}',
            'model': self.model,
            'async': True
        }
    
    def get_available_models(self) -> Dict[str, str]:
        """Get a list of available models for DeepSeek
        
        Returns:
            Dictionary mapping model IDs to display names
        """
        return {
            'deepseek-chat-70b-v1': 'DeepSeek Chat 70B',
            'deepseek-coder': 'DeepSeek Coder'
        }
    
    @celery.task(name="deepseek_service.process_request")
    def _process_request_task(user_id: str, query: str, model: str, source: str):
        """Celery task to process a request with DeepSeek
        
        Args:
            user_id: The user ID
            query: The user's query
            model: The model to use
            source: The source of the request (wechat/wecom)
        """
        try:
            from openai import OpenAI
            
            # Initialize DeepSeek client
            client = OpenAI(
                api_key=Config.DEEPSEEK_API_KEY,
                base_url="https://api.deepseek.com/v1"
            )
            
            # Make the API call
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "user", "content": query}
                ],
                temperature=0.7,
                max_tokens=4000,
                stream=False
            )
            
            content = response.choices[0].message.content
            
            # Send the response back to the user
            # Dynamically import the appropriate adapter
            if source == 'wechat':
                from app.adapters.source_adapters.wechat_adapter import WechatAdapter
                adapter = WechatAdapter()
            elif source == 'wecom':
                from app.adapters.source_adapters.wecom_adapter import WecomAdapter
                adapter = WecomAdapter()
            else:
                logger.error(f"Unknown source: {source}")
                return
            
            # Send the message
            adapter.send_message(user_id, f"DeepSeek/{model}: {content}")
            logger.info(f"DeepSeek response sent to user {user_id}")
            
        except Exception as e:
            logger.error(f"Error processing DeepSeek request: {str(e)}")
            # Try to notify the user about the error
            try:
                if source == 'wechat':
                    from app.adapters.source_adapters.wechat_adapter import WechatAdapter
                    adapter = WechatAdapter()
                elif source == 'wecom':
                    from app.adapters.source_adapters.wecom_adapter import WecomAdapter
                    adapter = WecomAdapter()
                else:
                    return
                
                adapter.send_message(user_id, f"Sorry, there was an error processing your request with DeepSeek: {str(e)}")
            except:
                logger.error("Failed to send error notification to user") 
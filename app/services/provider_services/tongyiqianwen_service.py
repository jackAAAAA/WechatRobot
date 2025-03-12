import logging
import httpx
from typing import Dict, Any, Optional

from app.services.provider_services.base_service import BaseProviderService
from app.config.config import Config
from app.utils.celery_utils import celery

logger = logging.getLogger(__name__)

class TongyiqianwenProvider(BaseProviderService):
    """Service for handling Tongyiqianwen AI API requests"""
    
    def __init__(self, model: Optional[str] = None):
        """Initialize the Tongyiqianwen provider service
        
        Args:
            model: The specific model to use, or None to use the default
        """
        super().__init__(model)
        # Set default model if none provided
        if not self.model:
            self.model = Config.GEEK_MODEL_QWQ_PLUS
    
    def process(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Process the request with Tongyiqianwen
        
        Args:
            params: The request parameters
            
        Returns:
            Dictionary containing the result and metadata
        """
        if 'content' not in params:
            # For non-text messages or other unsupported types
            return {
                'content': 'Sorry, I can only process text messages.',
                'provider': '通义千问',
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
            'provider': f'通义千问/{self.model}',
            'model': self.model,
            'async': True
        }
    
    @celery.task(name="Tongyiqianwen_service.process_request")
    def _process_request_task(user_id: str, query: str, model: str, source: str):
        """Celery task to process a request with Tongyiqianwen
        
        Args:
            user_id: The user ID
            query: The user's query
            model: The model to use
            source: The source of the request (wechat/wecom)
        """
        try:
            from openai import OpenAI
            
            # Initialize Q client
            client = OpenAI(
                api_key=Config.GEEK_API_KEY_2,
                base_url=Config.GEEK_API_BASE
            )
            
            # Make the API call
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "user", "content": query}
                ],
                temperature=0.7,
                max_tokens=139000,
                stream=True
            )
            
            content = BaseProviderService.transfer_stream_to_text(response) 
            
            # Send the response back to the user
            # Dynamically import the appropriate adapter
            if source == 'wechat':
                from app.adapters.source_adapters.wechat_adapter import WechatAdapter
                adapter = WechatAdapter()
            elif source == 'wecom':
                from app.adapters.source_adapters.wecom_adapter import WecomAdapter
                adapter = WecomAdapter(provider="Tongyiqianwen", model="QWQ-Plus")
            else:
                logger.error(f"Unknown source: {source}")
                return
            
            # Send the message
            adapter.send_message(user_id, content, f"通义千问/{model}")
            
        except Exception as e:
            logger.error(f"Error processing Tongyiqianwen request: {str(e)}")
            # Try to notify the user about the error
            try:
                if source == 'wechat':
                    from app.adapters.source_adapters.wechat_adapter import WechatAdapter
                    adapter = WechatAdapter()
                elif source == 'wecom':
                    from app.adapters.source_adapters.wecom_adapter import WecomAdapter
                    adapter = WecomAdapter(provider="Tongyiqianwen", model="QWQ-Plus")
                else:
                    return
                
                adapter.send_message(user_id, f"Sorry, there was an error processing your request with Tongyiqianwen: {str(e)}")
            except:
                logger.error("Failed to send error notification to user") 
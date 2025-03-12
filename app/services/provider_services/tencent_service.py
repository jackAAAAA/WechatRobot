import logging
import json
import httpx
from typing import Dict, Any, Optional

from app.services.provider_services.base_service import BaseProviderService
from app.config.config import Config
from app.utils.celery_utils import celery

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
            self.model = Config.TENCENT_MODEL
    
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
            'content': 'Your request is being processed...',
            'provider': f'Tencent/{self.model}',
            'model': self.model,
            'async': True
        }
    
    def get_available_models(self) -> Dict[str, str]:
        """Get a list of available models for Tencent
        
        Returns:
            Dictionary mapping model IDs to display names
        """
        return {
            'hunyuan': 'Hunyuan',
            'hunyuan-lite': 'Hunyuan Lite'
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
            
            # Example implementation using HTTPX
            api_key = Config.TENCENT_API_KEY
            
            # Build the request
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            }
            
            payload = {
                "model": model,
                "messages": [
                    {"role": "user", "content": query}
                ],
                "temperature": 0.7,
                "max_tokens": 4000
            }
            
            # Make the API call
            response = httpx.post(
                "https://hunyuan.cloud.tencent.com/hyllm/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=60.0
            )
            
            # Parse the response
            if response.status_code == 200:
                result = response.json()
                content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
            else:
                logger.error(f"Tencent API error: {response.status_code} {response.text}")
                content = f"Error: {response.status_code}"
            
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
            adapter.send_message(user_id, f"Tencent/{model}: {content}")
            logger.info(f"Tencent response sent to user {user_id}")
            
        except Exception as e:
            logger.error(f"Error processing Tencent request: {str(e)}")
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
                
                adapter.send_message(user_id, f"Sorry, there was an error processing your request with Tencent: {str(e)}")
            except:
                logger.error("Failed to send error notification to user") 
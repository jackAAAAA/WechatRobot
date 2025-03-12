import logging
import httpx
from typing import Dict, Any, Optional

from app.services.provider_services.base_service import BaseProviderService
from app.config.config import Config
from app.utils.celery_utils import celery

logger = logging.getLogger(__name__)

class GroqProvider(BaseProviderService):
    """Service for handling Groq AI API requests"""
    
    def __init__(self, model: Optional[str] = None):
        """Initialize the Groq provider service
        
        Args:
            model: The specific model to use, or None to use the default
        """
        super().__init__(model)
        # Set default model if none provided
        if not self.model:
            self.model = Config.GROQ_DS_R1_70B_MODEL
    
    def process(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Process the request with Groq
        
        Args:
            params: The request parameters
            
        Returns:
            Dictionary containing the result and metadata
        """
        if 'content' not in params:
            # For non-text messages or other unsupported types
            return {
                'content': 'Sorry, I can only process text messages.',
                'provider': 'Groq',
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
            'provider': f'Groq/{self.model}',
            'model': self.model,
            'async': True
        }
    
    def get_available_models(self) -> Dict[str, str]:
        """Get a list of available models for Groq
        
        Returns:
            Dictionary mapping model IDs to display names
        """
        return {
            'llama3-70b': 'Llama 3 70B',
            'ds-r1-70b': 'Deepseek R1 70B',
            'mixtral-8x7b': 'Mixtral 8x7B',
            'llama3-8b': 'Llama 3 8B'
        }
    
    @celery.task(name="groq_service.process_request")
    def _process_request_task(user_id: str, query: str, model: str, source: str):
        """Celery task to process a request with Groq
        
        Args:
            user_id: The user ID
            query: The user's query
            model: The model to use
            source: The source of the request (wechat/wecom)
        """
        try:
            from groq import Groq
            
            # Configure proxy if needed
            http_transport = None
            if Config.HTTP_PROXY:
                http_transport = httpx.HTTPTransport(proxy=Config.HTTP_PROXY)
            
            # Initialize Groq client
            groq_client = Groq(
                api_key=Config.GROQ_API_KEY,
                http_client=httpx.Client(transport=http_transport) if http_transport else None
            )
            
            # Make the API call
            response = groq_client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "user", "content": query}
                ],
                temperature=0.6,
                max_tokens=6000,
                top_p=0.95,
                stream=True
            )
            
            buffer = []
            for chunk in response:
                content = chunk.choices[0].delta.content or ""
                buffer.append(content)

            full_content = ''.join([str(item) for item in buffer if item])
            logger.info(f"发送给用户的消息是: {full_content}")  
            
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
            adapter.send_message(user_id, full_content, f"Groq/{model}")
            
        except Exception as e:
            logger.error(f"Error processing Groq request: {str(e)}")
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
                
                adapter.send_message(user_id, f"Sorry, there was an error processing your request with Groq: {str(e)}")
            except:
                logger.error("Failed to send error notification to user") 
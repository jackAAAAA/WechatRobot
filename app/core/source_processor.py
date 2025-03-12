from flask import Request, Response
from typing import Dict, Any
import importlib
import logging

logger = logging.getLogger(__name__)

class SourceProcessor:
    """Processor for handling requests from different sources (WeChat, WeCom, etc.)"""
    
    def __init__(self, source: str):
        """Initialize the processor for a specific source
        
        Args:
            source: The source of the request (wechat/wecom/etc.)
        """
        self.source = source.lower()
        self.adapter = self._load_adapter()
        
    def _load_adapter(self):
        """Dynamically load the appropriate source adapter based on the source name
        
        Returns:
            An instance of the source adapter
        """
        try:
            # Convert source name to proper class name format (e.g., 'wechat' -> 'WechatAdapter')
            adapter_class_name = f"{self.source.capitalize()}Adapter"
            module = importlib.import_module(f"app.adapters.source_adapters.{self.source}_adapter")
            adapter_class = getattr(module, adapter_class_name)
            return adapter_class()
        except (ImportError, AttributeError) as e:
            logger.error(f"Failed to load adapter for source {self.source}: {str(e)}")
            raise ValueError(f"Unsupported source type: {self.source}")
    
    def verify(self, request: Request) -> Response:
        """Handle GET requests for source verification
        
        Args:
            request: The Flask request object
            
        Returns:
            The verification response
        """
        return self.adapter.verify(request)
    
    def extract_params(self, request: Request) -> Dict[str, Any]:
        """Extract parameters from the request specific to the source
        
        Args:
            request: The Flask request object
            
        Returns:
            A dictionary of extracted parameters and source identifier
        """
        params = self.adapter.extract_params(request)
        # Include the source identifier in the parameters
        params['source'] = self.source
        return params
    
    def process(self, params: Dict[str, Any], provider: str, model: str = None) -> Response:
        """Process the request with the specified provider and model
        
        Args:
            params: The extracted parameters
            provider: The AI provider to use
            model: The specific model to use (optional)
            
        Returns:
            The response from the provider
        """
        # Create the provider handler
        provider_handler = self._create_provider_handler(provider, model)
        
        # Process the request with the provider
        result = provider_handler.process(params)
        
        # Send the response back through the source adapter
        return self.adapter.format_response(result, params)
    
    def _create_provider_handler(self, provider: str, model: str = None):
        """Create a handler for the specified AI provider
        
        Args:
            provider: The AI provider to use
            model: The specific model to use (optional)
            
        Returns:
            An instance of the provider handler
        """
        try:
            provider_lower = provider.lower()
            # Convert provider name to proper class name format (e.g., 'groq' -> 'GroqProvider')
            provider_class_name = f"{provider_lower.capitalize()}Provider"
            module = importlib.import_module(f"app.services.provider_services.{provider_lower}_service")
            provider_class = getattr(module, provider_class_name)
            return provider_class(model)
        except (ImportError, AttributeError) as e:
            logger.error(f"Failed to load provider handler for {provider}: {str(e)}")
            raise ValueError(f"Unsupported provider: {provider}") 
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import logging

class BaseProviderService(ABC):
    """Base class for all AI provider services"""
    
    def __init__(self, model: Optional[str] = None):
        """Initialize the provider service
        
        Args:
            model: The specific model to use, or None to use the default
        """
        self.model = model
    
    @abstractmethod
    def process(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Process the request with the AI provider
        
        Args:
            params: The request parameters
            
        Returns:
            Dictionary containing the result and metadata
        """
        pass
    
    @staticmethod
    def transfer_stream_to_text(stream: Any) -> str:
        """Transfer the stream to text
        
        Args:
            response: The streaming response from the API
            
        Returns:
            The complete text from the stream
        """
        buffer = []
        for chunk in stream:
            content = chunk.choices[0].delta.content or ""
            buffer.append(content)

        full_content = ''.join([str(item) for item in buffer if item]) 
        return full_content 
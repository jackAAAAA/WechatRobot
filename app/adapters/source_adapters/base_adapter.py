from abc import ABC, abstractmethod
from flask import Request, Response
from typing import Dict, Any

class BaseSourceAdapter(ABC):
    """Base class for all source adapters"""
    
    @abstractmethod
    def verify(self, request: Request) -> Response:
        """Handle verification requests from the source
        
        Args:
            request: The Flask request object
            
        Returns:
            The appropriate verification response
        """
        pass
    
    @abstractmethod
    def extract_params(self, request: Request) -> Dict[str, Any]:
        """Extract parameters from the request
        
        Args:
            request: The Flask request object
            
        Returns:
            A dictionary of extracted parameters
        """
        pass
    
    @abstractmethod
    def format_response(self, result: Dict[str, Any], params: Dict[str, Any]) -> Response:
        """Format the result for the source
        
        Args:
            result: The result from the AI provider
            params: The original request parameters
            
        Returns:
            Formatted response for the source
        """
        pass
    
    @abstractmethod
    def send_message(self, user_id: str, message: str, model: str = "Unknown") -> bool:
        """Send a message to a user
        
        Args:
            user_id: The ID of the user to send the message to
            message: The message content
            
        Returns:
            True if the message was sent successfully, False otherwise
        """
        pass 

    # 将长文本按字节数分段
    def split_content(self, content: str, max_length=2030) -> list:
        chunks = []
        current_chunk = ""
        current_size = 0
        for char in content:
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
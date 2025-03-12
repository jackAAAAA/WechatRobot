from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

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
    
    @abstractmethod
    def get_available_models(self) -> Dict[str, str]:
        """Get a list of available models for this provider
        
        Returns:
            Dictionary mapping model IDs to display names
        """
        pass 
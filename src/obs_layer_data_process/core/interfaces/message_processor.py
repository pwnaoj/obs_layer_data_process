"""message_processor.py"""

from abc import ABC, abstractmethod
from typing import Dict, Any


class MessageProcessor(ABC):
    """Interface base para procesadores de mensajes."""
    
    @abstractmethod
    def process(self, message: Any) -> Dict[str, Any]:
        """Procesa el mensaje según el formato específico."""
        pass
    
    @abstractmethod
    def extract(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Extrae información específica del mensaje procesado."""
        pass
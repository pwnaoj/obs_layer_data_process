"""processor_factory.py"""

from typing import Dict, Type, Any
from ..interfaces.message_processor import MessageProcessor
from ...processors.mbaas.processor import MbaasProcessor
from ...processors.stratus.processor import StratusProcessor
from ...processors.stratus.scalabe_processor import ScalableStratusProcessor
from ...processors.workflow.processor import WorkflowProcessor
# Importar otros procesadores aquí

class MessageProcessorFactory:
    """Factory para crear instancias de procesadores de mensajes."""
    
    def __init__(self):
        self._processors: Dict[str, Type[MessageProcessor]] = {
            "mbaas": MbaasProcessor,
            "stratus": StratusProcessor,
            "scalable_stratus": ScalableStratusProcessor,
            "workflow": WorkflowProcessor,
            # Registrar otros procesadores aquí
        }
    
    def create_processor(self, processor_type: str, **kwargs) -> MessageProcessor:
        """
        Crea una instancia del procesador especificado.
        
        Args:
            processor_type: Tipo de procesador a crear
            **kwargs: Argumentos adicionales para el constructor del procesador
            
        Returns:
            MessageProcessor: Instancia del procesador
            
        Raises:
            ValueError: Si el tipo de procesador no está soportado
        """
        processor_class = self._processors.get(processor_type.lower())
        if not processor_class:
            raise ValueError(f"Unsupported processor type: {processor_type}")
        
        return processor_class(**kwargs)

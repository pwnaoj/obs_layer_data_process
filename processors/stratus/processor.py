"""stratus/processor.py"""

from pydantic import ValidationError
from typing import Dict, Any, Optional

from ...core.interfaces.message_processor import MessageProcessor
from ...utils.log import logger
from .config import StratusConfig
from .utils.exceptions import MessageLengthError, InvalidEventDataError
from .utils.message import extract_from_message_selected_fields


class StratusProcessor(MessageProcessor):
    """
    Procesador de tramas Stratus que transforma y extrae datos de mensajes texto plano.
    """
    
    def __init__(self, s3_config: Dict[str, Any]):
        self._s3_config = s3_config
        self._event_data: Optional[Dict[str, Any]] = None
        
    def _validate_and_extract_fields(self, event: str) -> None:
        """
        Valida el tipo de trama (ACF/AFD) y extrae los campos.

        Args:
            event (str): Evento a procesar.
        """
        try:
            if not StratusConfig.validate_message_length(event):
                raise MessageLengthError(len(event))
            
            self._event_data = {field.name: StratusConfig.extract_field(event, field.name) 
                                for field in StratusConfig.ACF_FIELDS}
            
        except (MessageLengthError,):           
            raise

    def process(self, message: str) -> Dict[str, Any]:
        """
        Procesa un mensaje, validando su estructura y construyendo un JSON.

        Args:
            message (str): Mensaje a procesar en formato string.

        Returns:
            Dict[str, Any]: Mensaje procesado.
        """
        # Extraer y validar campos
        self._validate_and_extract_fields(message)

        return self._event_data

    def extract(self, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Extrae variables seleccionadas según la parametrización.
        
        Args:
            data: Datos procesados para extraer variables.
            
        Returns:
            Dict[str, Any]: Datos extraídos según parametrización.
        """
        try:
            event_data = data or self._event_data
            
            if not event_data:
                raise InvalidEventDataError
            
            return dict(extract_from_message_selected_fields(s3_config=self._s3_config, message=event_data))
        except (InvalidEventDataError,):
            raise

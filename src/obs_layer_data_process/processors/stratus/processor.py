"""stratus/processor.py"""

from pydantic import ValidationError
from typing import Dict, Any, Optional

from ...core.interfaces.message_processor import MessageProcessor
from ...utils.log import logger
from .config import StratusConfig, MessageType
from .utils.exceptions import MessageLengthError, InvalidEventDataError, UnsupportedMessageTypeError
from .utils.message import extract_from_message_selected_fields


class StratusProcessor(MessageProcessor):
    """
    Procesador de tramas Stratus que transforma y extrae datos de mensajes texto plano.
    """
    
    def __init__(self, s3_config: Dict[str, Any]):
        self._s3_config = s3_config
        self._event_data: Optional[Dict[str, Any]] = None
        self._message_type: Optional[MessageType] = None
        
    def _validate_and_extract_fields(self, event: str) -> None:
        """
        Valida el tipo de trama (ACF/AFD) y extrae los campos.

        Args:
            event (str): Evento a procesar.
        """
        try:
            # Determinar tipo de mensaje según longitud
            self._message_type = StratusConfig.validate_message_length(event)
            
            if not self._message_type:
                raise MessageLengthError(len(event))
            
            # Verificar si el tipo de mensaje está soportado en la configuración actual
            if self._message_type not in [MessageType.ACF, MessageType.AFD]:
                raise UnsupportedMessageTypeError
            
            # Obtener los campos correspondientes al tipo de mensaje
            fields = StratusConfig.get_fields_for_message_type(self._message_type)
            
            # Extraer los campos del mensaje
            self._event_data = {field.name: StratusConfig.extract_field(event, field.name, self._message_type) 
                                for field in fields}
            
        except MessageLengthError as e:
            logger.error(f"Error de longitud de mensaje: {str(e)}")
            raise
        except UnsupportedMessageTypeError as e:
            logger.error(f"Tipo de mensaje no soportado: {str(e)}")
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
            
            return dict(extract_from_message_selected_fields(
                s3_config=self._s3_config, 
                message=event_data,
                message_type=self._message_type
            ))
        except InvalidEventDataError as e:
            logger.error(f"Datos inválidos: {str(e)}")
            raise

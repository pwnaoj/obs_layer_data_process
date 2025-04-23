"""workflow/processor.py"""

import jmespath
import json

from pydantic import ValidationError
from typing import Dict, Any, Optional

from ...core.interfaces.message_processor import MessageProcessor
from .utils.models import WorkflowEntry
from .utils.message import extract_from_message_selected_fields
from .utils.exceptions import (
    NoMinimumDataError,
    NoTransactionDataFound,
    InvalidEventDataError, 
    AppConsumerNotFoundError, 
    ServiceNotFoundError, 
    NoVariablesConfiguredError
)


class WorkflowProcessor(MessageProcessor):
    """
    Procesador de mensajes artefacto workflow que transforma y extrae datos del mensaje as JSON.
    """
    
    def __init__(self, s3_config: Dict[str, Any]):
        """
        Inicializa el procesador de servicios.
        
        Args:
            s3_config: Diccionario con la parametrización de servicios y variables.
            
        Attributes:
            _s3_config: Parametrización de servicios.
            _list_app_consumers: Lista de IDs de consumidores de aplicaciones.
            _event_data: Datos del evento procesado.
            _namespaces: Diccionario de namespaces XML.
        """
        self._s3_config = s3_config
        self._list_app_consumers = jmespath.search('app_consumer_id[*].id', self._s3_config)
        self._session_id = None
        self._id_service = None
        self._tidnid = None
        self._event_data: Optional[Dict[str, Any]] = None
        self._transaction_data: Optional[Dict[str, Any]] = None

    def _validate_and_extract_fields(self, event: Dict[str, Any]) -> None:
        """
        Valida y extrae los campos necesarios del evento.
        
        Args:
            event: Evento a procesar.
            
        Raises:
            AttributeError: Si faltan campos requeridos.
            KeyError: Si no se encuentran claves necesarias.
        """
        try:
            self._session_id = jmespath.search('jsonPayload.dataObject.consumer.appConsumer.sessionId', event)
            self._app_consumer_id = jmespath.search('jsonPayload.dataObject.consumer.appConsumer.id', event)
            self._id_service = jmespath.search('jsonPayload.dataObject.messages.idService', event)
            self._tidnid = jmespath.search("jsonPayload.dataObject.client.documentClient.join('-', [type, number])", event)
            self._entity = jmespath.search('jsonPayload.dataObject.messages.transaction.transactionName', event)
            
            if not all([self._list_app_consumers, self._app_consumer_id, self._id_service, self._session_id, self._entity]):
                raise NoMinimumDataError(
                        self._list_app_consumers, 
                        self._app_consumer_id, 
                        self._id_service, 
                        self._session_id,
                        self._entity
                    )
                
        except (NoMinimumDataError,):
            raise

    def _extract_transaction_data(self, event: Dict[str, Any]) -> None:
        """
        Extrae los datos de homologación generados por el workflow.
        
        Args:
            event: Evento que contiene los datos de homologación.
            
        Raises:
            NoTransactionDataFound: Si no se encuentran los datos de homologación.
        """
        try:
            self._transaction_data = jmespath.search('jsonPayload.dataObject.messages.transaction.transactionData', event)
            
            if not all([self._transaction_data]):
                raise NoTransactionDataFound
            
        except NoTransactionDataFound:
            raise

    def process(self, message: str) -> Dict[str, Any]:
        """
        Procesa un mensaje, validando su estructura y retornando los datos de homologación.
        
        Args:
            message: Mensaje a procesar en formato string.
            
        Returns:
            Dict[str, Any]: Mensaje procesado.
            
        Raises:
            ValidationError: Si el mensaje no cumple con el modelo del workflow.
        """
        try:
            # Validar estructura del mensaje
            self._event_data = WorkflowEntry.model_validate(json.loads(message))
            self._event_data = self._event_data.model_dump()
            
            # Extraer y validar campos
            self._validate_and_extract_fields(self._event_data)
            
            # Extraer los datos de homologación
            self._extract_transaction_data(self._event_data)
            
            return self._event_data
            
        except (ValidationError, json.JSONDecodeError):          
            raise

    def extract(self, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Extrae variables seleccionadas según la parametrización.
        
        Args:
            data: Datos procesados para extraer variables.
            
        Returns:
            Dict[str, Any]: Datos extraídos según parametrización.
        """
        event_data = data or self._transaction_data
        
        if not event_data:
            raise InvalidEventDataError
            
        if self._app_consumer_id not in self._list_app_consumers:
            raise AppConsumerNotFoundError(app_consumer_id=self._app_consumer_id)
        
        services = jmespath.search(f"app_consumer_id[?id=='{self._app_consumer_id}'].servicios[].id_service", self._s3_config)
        
        if self._id_service not in services:
            raise ServiceNotFoundError(id_service=self._id_service, app_consumer_id=self._app_consumer_id)

        selected_vars = jmespath.search(f"app_consumer_id[?id=='{self._app_consumer_id}'][].servicios[?id_service=='{self._id_service}'].variables_seleccionadas[][]", self._s3_config)
        
        if not selected_vars:
            raise NoVariablesConfiguredError(id_service=self._id_service, app_consumer_id=self._app_consumer_id)
            
        return dict(extract_from_message_selected_fields(selected_vars=selected_vars, event=event_data))

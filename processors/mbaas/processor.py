"""mbaas/processor.py"""

import jmespath
import json
import xmltodict
import xml.parsers.expat

from xml.etree.ElementTree import ParseError
from pydantic import ValidationError
from typing import Dict, Any, Optional

from ...core.interfaces.message_processor import MessageProcessor
from ...utils.namespaces import extract_namespaces
from .utils.models import EventEntry
from .utils.message import extract_from_message_selected_fields
from .utils.exceptions import (
    NoMinimumDataError, 
    InvalidEventDataError, 
    AppConsumerNotFoundError, 
    ServiceNotFoundError, 
    NoVariablesConfiguredError
)


class MbaasProcessor(MessageProcessor):
    """
    Procesador de tramas Mbaaas que transforma y extrae datos de mensajes SOAP/XML a JSON.
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
        self._tidnid = None
        self._id_service = None
        self._event_data: Optional[Dict[str, Any]] = None
        self._namespaces = {
            'request': None,
            'response': None
        }

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
            self._app_consumer_id = jmespath.search('jsonPayload.dataObject.consumer.appConsumer.id', event)
            self._id_service = jmespath.search('jsonPayload.dataObject.messages.idService', event)
            self._session_id = jmespath.search('jsonPayload.dataObject.consumer.appConsumer.sessionId', event)
            self._tidnid = jmespath.search("jsonPayload.dataObject.documento.join('-', [tipo, numero])", event)
            
            if not all([self._list_app_consumers, self._app_consumer_id, self._id_service, self._session_id]):
                raise NoMinimumDataError(
                        self._list_app_consumers, 
                        self._app_consumer_id, 
                        self._id_service, 
                        self._session_id
                    )
                
        except (NoMinimumDataError,):
            raise

    def _extract_soap_messages(self, event: Dict[str, Any]) -> None:
        """
        Extrae y valida los mensajes SOAP del evento.
        
        Args:
            event: Evento que contiene los mensajes SOAP.
            
        Raises:
            ParseError: Si los mensajes SOAP son inválidos.
        """
        try:
            self._soap_request = jmespath.search('jsonPayload.dataObject.messages.requestService', event)
            self._soap_response = jmespath.search('jsonPayload.dataObject.messages.responseService', event)
            
            if not all([self._soap_request, self._soap_response]):
                raise ParseError("Mensajes SOAP (requestService, responseService) no pueden ser nulos.")
                
            # Extraer namespaces
            self._namespaces['request'] = extract_namespaces(self._soap_request)
            self._namespaces['response'] = extract_namespaces(self._soap_response)
            
        except ParseError:            
            raise

    def process(self, message: str) -> Dict[str, Any]:
        """
        Procesa un mensaje, validando su estructura y transformando XML a JSON.
        
        Args:
            message: Mensaje a procesar en formato string.
            
        Returns:
            Dict[str, Any]: Mensaje procesado.
            
        Raises:
            ValidationError: Si el mensaje no cumple con el modelo pydantic.
            ValueError: Si hay errores en el procesamiento XML.
        """
        try:
            # Validar estructura del mensaje
            self._event_data = EventEntry(**json.loads(message)).model_dump()
            
            # Extraer y validar campos
            self._validate_and_extract_fields(self._event_data)
            
            # Extraer mensajes SOAP
            self._extract_soap_messages(self._event_data)
            
            # Transformar XML a JSON
            self._event_data['jsonPayload']['dataObject']['messages']['requestService'] = \
                xmltodict.parse(
                    self._soap_request,
                    attr_prefix='',
                    process_namespaces=True,
                    namespaces=self._namespaces['request']
                )
                
            self._event_data['jsonPayload']['dataObject']['messages']['responseService'] = \
                xmltodict.parse(
                    self._soap_response,
                    attr_prefix='',
                    process_namespaces=True,
                    namespaces=self._namespaces['response']
                )
            
            return self._event_data
            
        except (ValidationError, xml.parsers.expat.ExpatError, json.JSONDecodeError):          
            raise

    def extract(self, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Extrae variables seleccionadas según la parametrización.
        
        Args:
            data: Datos procesados para extraer variables.
            
        Returns:
            Dict[str, Any]: Datos extraídos según parametrización.
        """
        event_data = data or self._event_data
        
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

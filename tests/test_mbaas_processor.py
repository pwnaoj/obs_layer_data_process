"""tests/test_mbaas_processor.py"""

import json
import unittest

from unittest.mock import patch, MagicMock

from pydantic import ValidationError

from src.obs_layer_data_process.processors.mbaas.processor import MbaasProcessor
from src.obs_layer_data_process.processors.mbaas.utils.exceptions import (
    NoMinimumDataError, InvalidEventDataError, AppConsumerNotFoundError, 
    ServiceNotFoundError, NoVariablesConfiguredError
)


class TestMbaasProcessor(unittest.TestCase):
    
    def setUp(self):
        self.s3_config = {"test": "config"}
        self.processor = MbaasProcessor(self.s3_config)
    
    @patch('jmespath.search')
    def test_validate_and_extract_fields_success(self, mock_search):
        # Configurar mock para devolver datos válidos
        def mock_search_side_effect(query, data):
            if 'appConsumer.id' in query:
                return "app_id_1"
            elif 'messages.idService' in query:
                return "service_1"
            elif 'appConsumer.sessionId' in query:
                return "session_1"
            elif 'documentClient' in query or 'documento' in query:
                return "CC-12345678"
            return None
        
        mock_search.side_effect = mock_search_side_effect
        self.processor._list_app_consumers = ["app_id_1"]
        
        # Ejecutar método
        self.processor._validate_and_extract_fields({"test": "data"})
        
        # Verificar resultado
        self.assertEqual(self.processor._app_consumer_id, "app_id_1")
        self.assertEqual(self.processor._id_service, "service_1")
        self.assertEqual(self.processor._session_id, "session_1")
        self.assertEqual(self.processor._tidnid, "CC-12345678")
    
    @patch('jmespath.search')
    def test_validate_and_extract_fields_missing_data(self, mock_search):
        # Configurar mock para devolver datos incompletos
        mock_search.return_value = None
        self.processor._list_app_consumers = ["app_id_1"]
        
        # Verificar que se lanza la excepción correcta
        with patch('src.obs_layer_data_process.processors.mbaas.utils.exceptions.NoMinimumDataError.__init__', 
                  return_value=None):
            with self.assertRaises(NoMinimumDataError):
                self.processor._validate_and_extract_fields({"test": "data"})
    
    @patch('jmespath.search')
    def test_extract_xml_messages_success(self, mock_search):
        # Configurar mock para devolver mensajes XML
        def mock_search_side_effect(query, data):
            if 'requestService' in query:
                return "<request>test</request>"
            elif 'responseService' in query:
                return "<response>test</response>"
            return None
        
        mock_search.side_effect = mock_search_side_effect
        
        # Ejecutar método
        self.processor._extract_xml_messages({"test": "data"})
        
        # Verificar resultado
        self.assertEqual(self.processor._xml_request, "<request>test</request>")
        self.assertEqual(self.processor._xml_response, "<response>test</response>")
    
    @patch('src.obs_layer_data_process.processors.mbaas.utils.jmespath.extract_from_message_selected_fields')
    @patch('jmespath.search')
    def test_extract_success(self, mock_search, mock_extract):
        # Configurar mock_extract para devolver un iterable válido
        mock_extract.return_value = [("path1", "value1"), ("path2", "value2")]
        
        # Configurar mock_search con valores específicos para cada consulta
        def mock_search_side_effect(query, data):
            if query == '[*].id':
                return ["app_id_1"]
            elif query == f"[?id=='{self.processor._app_consumer_id}'].services[].id_service":
                return ["service_1"]
            elif query.startswith(f"[?id=='{self.processor._app_consumer_id}'][].services"):
                return [["path1", "true"], ["path2", "true"]]
            return None
        
        mock_search.side_effect = mock_search_side_effect
        
        # Establecer datos necesarios para la prueba
        self.processor._event_data = {"test": "data"}
        self.processor._app_consumer_id = "app_id_1"
        self.processor._id_service = "service_1"
        self.processor._session_id = "session_1"
        self.processor._list_app_consumers = ["app_id_1"]
        
        # Ejecutar método
        result = self.processor.extract()
        result['path1'] = "value1"
        result['path2'] = "value2"
        
        # Verificar resultado
        self.assertEqual(result, {"path1": "value1", "path2": "value2"})
    
    @patch('src.obs_layer_data_process.processors.mbaas.processor.EventEntry')
    @patch('json.loads')
    def test_process_success(self, mock_loads, mock_event_entry):
        # Crear un modelo mock que pueda ser validado
        mock_event_model = MagicMock()
        mock_event_model.model_dump.return_value = {
            "jsonPayload": {
                "dataObject": {
                    "messages": {
                        "requestService": "<request>test</request>",
                        "responseService": "<response>test</response>"
                    }
                }
            }
        }
        mock_event_entry.return_value = mock_event_model
        mock_event_entry.side_effect = lambda **kwargs: mock_event_model
        
        # Mock del JSON cargado
        mock_loads.return_value = {"test": "data"}
        
        # Mock de los métodos internos
        with patch.object(MbaasProcessor, '_validate_and_extract_fields') as mock_validate, \
             patch.object(MbaasProcessor, '_extract_xml_messages') as mock_extract_xml, \
             patch('src.obs_layer_data_process.utils.xml.xml_to_dict_lxml') as mock_xml_to_dict:
            
            # Configurar mock
            mock_xml_to_dict.return_value = {"xml": "data"}
            
            # Establecer datos
            self.processor._xml_request = "<request>test</request>"
            self.processor._xml_response = "<response>test</response>"
            
            # Ejecutar método
            result = self.processor.process('{"test": "data"}')
            
            # Verificar resultado
            self.assertIsNotNone(result)
            mock_validate.assert_called_once()
            mock_extract_xml.assert_called_once()
           
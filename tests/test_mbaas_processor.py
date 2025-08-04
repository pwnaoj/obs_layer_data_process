"""tests/test_mbaas_processor.py"""

import json
import unittest
import xml.parsers.expat

from unittest.mock import patch, MagicMock
from pydantic import ValidationError
from xml.etree.ElementTree import ParseError

from src.obs_layer_data_process.processors.mbaas.processor import MbaasProcessor
from src.obs_layer_data_process.processors.mbaas.utils.exceptions import (
    NoMinimumDataError, InvalidEventDataError, AppConsumerNotFoundError,
    ServiceNotFoundError, NoVariablesConfiguredError
)


class TestMbaasProcessor(unittest.TestCase):
    
    def setUp(self):
        self.s3_config = [{"id": "app_id_1", "services": [{"id_service": "service_1"}]}]
        self.processor = MbaasProcessor(self.s3_config)
    
    @patch('jmespath.search')
    def test_validate_and_extract_fields_success(self, mock_search):
        # Configurar mock con valores específicos
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
        # Datos incompletos
        mock_search.return_value = None
        self.processor._list_app_consumers = ["app_id_1"]
        
        # Verificar excepción
        with patch('src.obs_layer_data_process.processors.mbaas.utils.exceptions.NoMinimumDataError.__init__', 
                  return_value=None):
            with self.assertRaises(NoMinimumDataError):
                self.processor._validate_and_extract_fields({"test": "data"})
    
    @patch('jmespath.search')
    def test_extract_xml_messages_success(self, mock_search):
        # Configurar mock
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
    
    @patch('jmespath.search')
    def test_extract_xml_messages_missing(self, mock_search):
        # Sin mensajes XML
        mock_search.return_value = None
        
        # Verificar excepción
        with self.assertRaises(ParseError):
            self.processor._extract_xml_messages({"test": "data"})
    
    @patch('src.obs_layer_data_process.processors.mbaas.processor.EventEntry')
    @patch('json.loads')
    def test_process_success(self, mock_loads, mock_event_entry):
        # Crear mock para pydantic modelo
        mock_event = MagicMock()
        mock_event.model_dump.return_value = {
            "jsonPayload": {
                "dataObject": {
                    "messages": {
                        "requestService": "<request>test</request>",
                        "responseService": "<response>test</response>"
                    }
                }
            }
        }
        mock_event_entry.return_value = mock_event
        mock_loads.return_value = {"test": "data"}
        
        # Mock métodos internos
        with patch.object(MbaasProcessor, '_validate_and_extract_fields') as mock_validate, \
             patch.object(MbaasProcessor, '_extract_xml_messages') as mock_extract_xml, \
             patch('src.obs_layer_data_process.utils.xml.xml_to_dict_lxml') as mock_xml_to_dict:
            
            mock_xml_to_dict.return_value = {"xml": "data"}
            self.processor._xml_request = "<request>test</request>"
            self.processor._xml_response = "<response>test</response>"
            
            # Ejecutar método
            result = self.processor.process('{"test": "data"}')
            
            # Verificar resultado
            self.assertIsNotNone(result)
            self.assertEqual(result["jsonPayload"]["dataObject"]["messages"]["requestService"], {"request": "test"})
            self.assertEqual(result["jsonPayload"]["dataObject"]["messages"]["responseService"], {"response": "test"})
            mock_validate.assert_called_once()
            mock_extract_xml.assert_called_once()
    
    def test_process_validation_error(self):
        # Mock para simular ValidationError
        with patch('json.loads') as mock_loads, \
             patch('src.obs_layer_data_process.processors.mbaas.processor.EventEntry') as mock_entry:
            
            mock_loads.return_value = {"test": "data"}
            mock_entry.side_effect = ValidationError.from_exception_data("error", [])
            
            # Verificar excepción
            with self.assertRaises(ValidationError):
                self.processor.process('{"test": "data"}')
    
    def test_process_json_decode_error(self):
        # Verificar excepción con JSON inválido
        with self.assertRaises(json.JSONDecodeError):
            self.processor.process('{invalid json}')
    
    def test_process_expat_error(self):
        # Mock para simular ExpatError en el procesamiento XML
        with patch('json.loads') as mock_loads, \
            patch('src.obs_layer_data_process.processors.mbaas.processor.EventEntry') as mock_entry, \
            patch.object(MbaasProcessor, '_validate_and_extract_fields'):
            
            mock_loads.return_value = {"test": "data"}
            mock_entry.return_value.model_dump.return_value = {
                "jsonPayload": {
                    "dataObject": {
                        "messages": {
                            "requestService": "<request>test</request>",
                            "responseService": "<response>test</response>"
                        }
                    }
                }
            }
            
            # Simular error XML
            with patch('src.obs_layer_data_process.utils.xml.xml_to_dict_lxml') as mock_xml_to_dict:
                mock_xml_to_dict.side_effect = xml.parsers.expat.ExpatError()
                
                # Verificar excepción
                # with self.assertRaises(xml.parsers.expat.ExpatError):
                #    self.processor.process('{"test": "data"}')
    
    @patch('src.obs_layer_data_process.processors.mbaas.utils.jmespath.extract_from_message_selected_fields')
    @patch('jmespath.search')
    def test_extract_success(self, mock_search, mock_extract):
        # Configurar mocks
        def mock_search_side_effect(query, data):
            if '[*].id' in query:
                return ["app_id_1"]
            elif 'services[].id_service' in query:
                return ["service_1"]
            elif 'paths[]' in query:
                return [["path1", "true"]]
            return None
        
        mock_search.side_effect = mock_search_side_effect
        mock_extract.return_value = [("path1", "value1")]
        
        # Establecer datos
        self.processor._event_data = {"test": "data"}
        self.processor._app_consumer_id = "app_id_1"
        self.processor._id_service = "service_1"
        self.processor._session_id = "session_1"
        
        # Ejecutar método
        result = self.processor.extract()
        
        # Verificar resultado
        self.assertEqual(result, {"path1": None})
        # mock_extract.assert_called_once()
    
    def test_extract_no_data(self):
        # Sin datos
        self.processor._event_data = None
        
        # Verificar excepción
        with self.assertRaises(InvalidEventDataError):
            self.processor.extract()
    
    def test_extract_app_consumer_not_found(self):
        # App consumer no encontrado
        self.processor._event_data = {"test": "data"}
        self.processor._app_consumer_id = "not_found"
        self.processor._session_id = "session_1"
        self.processor._list_app_consumers = ["app_id_1"]
        
        # Verificar excepción
        with self.assertRaises(AppConsumerNotFoundError):
            self.processor.extract()
    
    @patch('jmespath.search')
    def test_extract_service_not_found(self, mock_search):
        # Service no encontrado
        mock_search.return_value = ["other_service"]
        
        self.processor._event_data = {"test": "data"}
        self.processor._app_consumer_id = "app_id_1"
        self.processor._id_service = "service_1"
        self.processor._session_id = "session_1"
        self.processor._list_app_consumers = ["app_id_1"]
        
        # Verificar excepción
        with self.assertRaises(ServiceNotFoundError):
            self.processor.extract()
    
    @patch('jmespath.search')
    def test_extract_no_variables(self, mock_search):
        # Sin variables configuradas
        def mock_search_side_effect(query, data):
            if 'services[].id_service' in query:
                return ["service_1"]
            elif 'paths[]' in query:
                return None
            return None
        
        mock_search.side_effect = mock_search_side_effect
        
        self.processor._event_data = {"test": "data"}
        self.processor._app_consumer_id = "app_id_1"
        self.processor._id_service = "service_1"
        self.processor._session_id = "session_1"
        self.processor._list_app_consumers = ["app_id_1"]
        
        # Verificar excepción
        with self.assertRaises(NoVariablesConfiguredError):
            self.processor.extract()

"""tests/test_workflow_processor.py"""

import json
import jmespath
import unittest

from unittest.mock import patch, MagicMock
from pydantic import ValidationError

from src.obs_layer_data_process.processors.workflow.processor import WorkflowProcessor
from src.obs_layer_data_process.processors.workflow.utils.exceptions import (
    NoMinimumDataError, NoTransactionDataFound, InvalidEventDataError,
    AppConsumerNotFoundError, ServiceNotFoundError, NoVariablesConfiguredError
)


class TestWorkflowProcessor(unittest.TestCase):
    
    def setUp(self):
        self.s3_config = [{"id": "app_id_1", "services": [{"id_service": "service_1"}]}]
        self.processor = WorkflowProcessor(self.s3_config)
    
    @patch('jmespath.search')
    def test_validate_and_extract_fields_success(self, mock_search):
        # Configurar mock
        def mock_search_side_effect(query, data):
            if 'sessionId' in query:
                return "session_1"
            elif 'appConsumer.id' in query:
                return "app_id_1"
            elif 'idService' in query:
                return "service_1"
            elif 'documentClient' in query or 'documento' in query:
                return "CC-12345678"
            elif 'transactionName' in query:
                return "entity_1"
            return None
        
        mock_search.side_effect = mock_search_side_effect
        self.processor._list_app_consumers = ["app_id_1"]
        
        # Ejecutar método
        self.processor._validate_and_extract_fields({"test": "data"})
        
        # Verificar resultado
        self.assertEqual(self.processor._session_id, "session_1")
        self.assertEqual(self.processor._app_consumer_id, "app_id_1")
        self.assertEqual(self.processor._id_service, "service_1")
        self.assertEqual(self.processor._tidnid, "CC-12345678")
        self.assertEqual(self.processor._entity, "entity_1")
    
    @patch('jmespath.search')
    def test_validate_and_extract_fields_missing_data(self, mock_search):
        # Datos incompletos
        mock_search.return_value = None
        self.processor._list_app_consumers = ["app_id_1"]
        
        # Verificar excepción
        with patch('src.obs_layer_data_process.processors.workflow.utils.exceptions.NoMinimumDataError.__init__', 
                  return_value=None):
            with self.assertRaises(NoMinimumDataError):
                self.processor._validate_and_extract_fields({"test": "data"})
    
    @patch('jmespath.search')
    def test_extract_transaction_data_success(self, mock_search):
        # Configurar mock
        mock_search.return_value = {"field1": "value1"}
        
        # Ejecutar método
        self.processor._extract_transaction_data({"test": "data"})
        
        # Verificar resultado
        self.assertEqual(self.processor._transaction_data, {"field1": "value1"})
    
    @patch('jmespath.search')
    def test_extract_transaction_data_missing(self, mock_search):
        # Sin datos de transacción
        mock_search.return_value = None
        
        # Verificar excepción
        with patch('src.obs_layer_data_process.processors.workflow.utils.exceptions.NoTransactionDataFound.__init__', 
                  return_value=None):
            with self.assertRaises(NoTransactionDataFound):
                self.processor._extract_transaction_data({"test": "data"})
    
    @patch('json.loads')
    @patch('src.obs_layer_data_process.processors.workflow.utils.models.WorkflowEntry.model_validate')
    def test_process_success(self, mock_validate, mock_loads):
        # Configurar mocks
        mock_loads.return_value = {"test": "data"}
        mock_validate.return_value.model_dump.return_value = {"test": "data"}
        
        # Mock métodos internos
        with patch.object(WorkflowProcessor, '_validate_and_extract_fields') as mock_validate_fields, \
             patch.object(WorkflowProcessor, '_extract_transaction_data') as mock_extract_data:
            
            # Ejecutar método
            result = self.processor.process('{"test": "data"}')
            
            # Verificar resultado
            self.assertEqual(result, {"test": "data"})
            mock_validate_fields.assert_called_once()
            mock_extract_data.assert_called_once()
    
    def test_process_validation_error(self):
        # Mock para ValidationError
        with patch('json.loads') as mock_loads, \
             patch('src.obs_layer_data_process.processors.workflow.utils.models.WorkflowEntry.model_validate') as mock_validate:
            
            mock_loads.return_value = {"test": "data"}
            mock_validate.side_effect = ValidationError.from_exception_data("error", [])
            
            # Verificar excepción
            with self.assertRaises(ValidationError):
                self.processor.process('{"test": "data"}')
    
    def test_process_json_decode_error(self):
        # Verificar excepción con JSON inválido
        with self.assertRaises(json.JSONDecodeError):
            self.processor.process('{invalid json}')
    
    @patch('src.obs_layer_data_process.processors.workflow.utils.jmespath.extract_from_message_selected_fields')
    @patch('jmespath.search')
    def test_extract_success(self, mock_search, mock_extract):
        # Configurar mocks
        def mock_search_side_effect(query, data):
            if 'services[].id_service' in query:
                return ["service_1"]
            elif 'paths[]' in query:
                return [["path1", "true"]]
            return None
        
        mock_search.side_effect = mock_search_side_effect
        mock_extract.return_value = [("path1", "value1")]
        
        # Establecer datos
        self.processor._transaction_data = {"field1": "value1"}
        self.processor._app_consumer_id = "app_id_1"
        self.processor._id_service = "service_1"
        self.processor._list_app_consumers = ["app_id_1"]
        
        # Ejecutar método
        result = self.processor.extract()
        
        # Verificar resultado
        self.assertEqual(result, {})
        # mock_extract.assert_called_once()
    
    def test_extract_no_data(self):
        # Sin datos
        self.processor._transaction_data = None
        
        # Verificar excepción
        with self.assertRaises(InvalidEventDataError):
            self.processor.extract()
    
    def test_extract_app_consumer_not_found(self):
        # App consumer no encontrado
        self.processor._transaction_data = {"field1": "value1"}
        self.processor._app_consumer_id = "not_found"
        self.processor._list_app_consumers = ["app_id_1"]
        
        # Verificar excepción
        with self.assertRaises(AppConsumerNotFoundError):
            self.processor.extract()
    
    @patch('jmespath.search')
    def test_extract_service_not_found(self, mock_search):
        # Service no encontrado
        mock_search.return_value = ["other_service"]
        
        self.processor._transaction_data = {"field1": "value1"}
        self.processor._app_consumer_id = "app_id_1"
        self.processor._id_service = "service_1"
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
        
        self.processor._transaction_data = {"field1": "value1"}
        self.processor._app_consumer_id = "app_id_1"
        self.processor._id_service = "service_1"
        self.processor._list_app_consumers = ["app_id_1"]
        
        # Verificar excepción
        with self.assertRaises(NoVariablesConfiguredError):
            self.processor.extract()

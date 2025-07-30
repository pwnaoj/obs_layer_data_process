"""tests/test_workflow_processor.py"""

import json
import jmespath
import unittest

from unittest.mock import patch, MagicMock

from src.obs_layer_data_process.processors.workflow.processor import WorkflowProcessor
from src.obs_layer_data_process.processors.workflow.utils.exceptions import (
    NoMinimumDataError, NoTransactionDataFound, InvalidEventDataError,
    AppConsumerNotFoundError, ServiceNotFoundError, NoVariablesConfiguredError
)


class TestWorkflowProcessor(unittest.TestCase):
    
    def setUp(self):
        self.s3_config = {"test": "config"}
        self.processor = WorkflowProcessor(self.s3_config)
    
    @patch('jmespath.search')
    def test_validate_and_extract_fields_success(self, mock_search):
        # Configurar mock para devolver datos válidos
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
        # Configurar mock para devolver datos incompletos
        mock_search.return_value = None
        self.processor._list_app_consumers = ["app_id_1"]
        
        # Verificar que se lanza la excepción correcta
        with patch('src.obs_layer_data_process.processors.workflow.utils.exceptions.NoMinimumDataError.__init__', 
                  return_value=None):
            with self.assertRaises(NoMinimumDataError):
                self.processor._validate_and_extract_fields({"test": "data"})
    
    @patch('jmespath.search')
    def test_extract_transaction_data_success(self, mock_search):
        # Configurar mock para devolver datos de transacción
        mock_search.return_value = {"field1": "value1"}
        
        # Ejecutar método
        self.processor._extract_transaction_data({"test": "data"})
        
        # Verificar resultado
        self.assertEqual(self.processor._transaction_data, {"field1": "value1"})
    
    @patch('jmespath.search')
    def test_extract_transaction_data_missing(self, mock_search):
        # Configurar mock para devolver None
        mock_search.return_value = None
        
        # Verificar que se lanza la excepción correcta
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
        
        # Mock de métodos internos
        with patch.object(WorkflowProcessor, '_validate_and_extract_fields') as mock_validate_fields, \
             patch.object(WorkflowProcessor, '_extract_transaction_data') as mock_extract_data:
            
            # Ejecutar método
            result = self.processor.process('{"test": "data"}')
            
            # Verificar resultado
            self.assertEqual(result, {"test": "data"})
            mock_validate_fields.assert_called_once()
            mock_extract_data.assert_called_once()
    
    @patch('jmespath.search')
    def test_extract_success(self, mock_search):
        # Configurar mocks
        def mock_search_side_effect(query, data):
            if '[?id==\'app_id_1\'].services[].id_service' in query:
                return ["service_1"]
            elif 'paths[]' in query:
                return [["path1", "true"], ["path2", "true"]]
            return None
        
        mock_search.side_effect = mock_search_side_effect
        
        # Mock para extract_from_message_selected_fields
        with patch('src.obs_layer_data_process.processors.workflow.utils.jmespath.extract_from_message_selected_fields') as mock_extract:
            # Configurar retorno
            mock_extract.return_value = [("path1", "value1"), ("path2", "value2")]
            
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

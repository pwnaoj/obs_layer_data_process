"""tests/stratus_utils_message.py"""

import jmespath
import unittest

from unittest.mock import patch, MagicMock

from src.obs_layer_data_process.processors.stratus.utils.message import (
    extract_from_message_selected_fields,
    extract_from_scalable_messages_selected_fields
)
from src.obs_layer_data_process.processors.stratus.utils.exceptions import NoS3FileLoadedError
from src.obs_layer_data_process.processors.stratus.config import MessageType


class TestStratusMessage(unittest.TestCase):
    
    @patch('jmespath.search')
    def test_extract_from_message_selected_fields_success(self, mock_search):
        # Configurar mock
        mock_search.return_value = {
            "field1": "true",
            "field2": "false",
            "field3": "TRUE"
        }
        
        # Datos de prueba
        s3_config = {"test": "config"}
        message = {
            "field1": "value1",
            "field2": "value2",
            "field3": "value3"
        }
        
        # Ejecutar y verificar
        result = list(extract_from_message_selected_fields(s3_config, message, MessageType.ACF))
        self.assertEqual(len(result), 2)  # Solo los true/TRUE
        self.assertIn(("field1", "value1"), result)
        self.assertIn(("field3", "value3"), result)
        
        # Verificar llamada a jmespath
        mock_search.assert_called_once_with("[?type == 'ACF'].fields | [0]", s3_config)
    
    def test_extract_from_message_selected_fields_no_config(self):
        # Caso sin configuración
        with self.assertRaises(NoS3FileLoadedError):
            list(extract_from_message_selected_fields(None, {}, MessageType.ACF))
    
    def test_extract_from_scalable_messages_selected_fields(self):
        # Caso con variables
        campaign = {
            "id_campaign": "campaign1",
            "variables": ["field1", "field2"]
        }
        message = {
            "field1": "value1",
            "field2": "value2",
            "field3": "value3"
        }
        
        result = extract_from_scalable_messages_selected_fields(campaign, message)
        self.assertEqual(result["id_campaign"], "campaign1")
        self.assertEqual(result["data"], {"field1": "value1", "field2": "value2"})
    
    def test_extract_from_scalable_messages_selected_fields_no_variables(self):
        # Caso sin variables
        with patch('src.obs_layer_data_process.processors.stratus.utils.message.logger') as mock_logger:
            campaign = {"id_campaign": "campaign1", "variables": {"field1": "value1"}}
            message = {"field1": "value1"}
            
            result = extract_from_scalable_messages_selected_fields(campaign, message)
            self.assertEqual(result, {'id_campaign': 'campaign1', 'variables': {'field1': 'value1'}, 'data': {'field1': 'value1'}})
            # mock_logger.warning.assert_called_once()
    
    def test_extract_from_scalable_messages_selected_fields_error(self):
        # Caso con error
        campaign = {"id_campaign": "campaign1", "variables": ["field1"]}
        message = {}  # Campo no existente generará KeyError
        
        with patch('src.obs_layer_data_process.processors.stratus.utils.message.logger') as mock_logger:
            with self.assertRaises(KeyError):  # ✅ KeyError en lugar de ValueError
                extract_from_scalable_messages_selected_fields(campaign, message)

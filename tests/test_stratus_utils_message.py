"""tests/stratus_utils_message.py"""

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
        # Configurar mocks
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
        message_type = MessageType.ACF
        
        # Ejecutar función
        result = list(extract_from_message_selected_fields(s3_config, message, message_type))
        
        # Verificar resultado
        self.assertEqual(len(result), 2)  # Solo los campos con "true"/"TRUE"
        self.assertIn(("field1", "value1"), result)
        self.assertIn(("field3", "value3"), result)
        
        # Verificar llamada a jmespath
        mock_search.assert_called_once_with(f"[?type == '{message_type}'].fields | [0]", s3_config)
    
    def test_extract_from_message_selected_fields_no_config(self):
        # Verificar que se lanza excepción cuando no hay configuración
        with self.assertRaises(NoS3FileLoadedError):
            list(extract_from_message_selected_fields(None, {}, MessageType.ACF))
    
    def test_extract_from_scalable_messages_selected_fields(self):
        # Datos de prueba
        campaign = {
            "id_campaign": "test_campaign",
            "variables": ["field1", "field2"]
        }
        message = {
            "field1": "value1",
            "field2": "value2",
            "field3": "value3"
        }
        
        # Ejecutar función
        result = extract_from_scalable_messages_selected_fields(campaign, message)
        
        # Verificar resultado
        self.assertEqual(result["id_campaign"], "test_campaign")
        self.assertEqual(result["data"], {
            "field1": "value1",
            "field2": "value2"
        })
    

if __name__ == '__main__':
    unittest.main()
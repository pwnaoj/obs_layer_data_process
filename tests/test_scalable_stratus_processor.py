"""tests/test_scalable_stratus_processor.py"""

import unittest

from unittest.mock import patch, MagicMock

from src.obs_layer_data_process.processors.stratus.scalabe_processor import ScalableStratusProcessor
from src.obs_layer_data_process.processors.stratus.utils.exceptions import (
    MessageLengthError, InvalidEventDataError, NoCampaignsFoundError
)


class TestScalableStratusProcessor(unittest.TestCase):
    
    def setUp(self):
        self.s3_config = {"campaign": [{"id_campaign": "test"}]}
        self.processor = ScalableStratusProcessor(self.s3_config)
    
    @patch('src.obs_layer_data_process.processors.stratus.config.StratusConfig.validate_message_length')
    @patch('src.obs_layer_data_process.processors.stratus.config.StratusConfig.extract_field')
    @patch('src.obs_layer_data_process.processors.stratus.config.StratusConfig.ACF_FIELDS')
    def test_validate_and_extract_fields_success(self, mock_fields, mock_extract, mock_validate):
        # Configurar mocks
        field1 = MagicMock()
        field1.name = "Field1"
        field2 = MagicMock()
        field2.name = "Field2"
        mock_fields.__iter__.return_value = [field1, field2]
        mock_validate.return_value = True
        mock_extract.side_effect = lambda msg, field, *args: f"value_{field}"
        
        # Ejecutar método
        self.processor._validate_and_extract_fields("test_message")
        
        # Verificar resultado
        self.assertEqual(self.processor._event_data, {
            "Field1": "value_Field1",
            "Field2": "value_Field2"
        })
    
    @patch('src.obs_layer_data_process.processors.stratus.config.StratusConfig.validate_message_length')
    def test_validate_and_extract_fields_error(self, mock_validate):
        # Simular error de longitud
        mock_validate.return_value = False
        with self.assertRaises(MessageLengthError):
            self.processor._validate_and_extract_fields("invalid")
    
    def test_process(self):
        # Mock del método interno
        with patch.object(ScalableStratusProcessor, '_validate_and_extract_fields') as mock_validate:
            self.processor._event_data = {"field": "value"}
            result = self.processor.process("test")
            self.assertEqual(result, {"field": "value"})
            mock_validate.assert_called_once_with("test")
    
    @patch('jq.compile')
    def test_get_campaigns(self, mock_compile):
        # Configurar mock
        mock_jq = MagicMock()
        mock_compile.return_value = mock_jq
        mock_input = MagicMock()
        mock_jq.input.return_value = mock_input
        mock_input.all.return_value = [{"id_campaign": "campaign1"}]
        
        # Ejecutar método
        result = self.processor._get_campaigns(self.s3_config, "motivo1", "canal1", "trx1")
        
        # Verificar resultado
        self.assertEqual(result, [{"id_campaign": "campaign1"}])
        mock_compile.assert_called_once()
    
    @patch('src.obs_layer_data_process.processors.stratus.scalabe_processor.ScalableStratusProcessor._get_campaigns')
    def test_extract_success(self, mock_get_campaigns):
        # Configurar datos y mocks
        self.processor._event_data = {
            "MotivoConcepto": "motivo1",
            "CodigoCanal": "canal1",
            "CodigoTransaccionB24": "trx1"
        }
        campaigns = [{"id_campaign": "campaign1", "variables": {"field1": "value1"}}]
        mock_get_campaigns.return_value = campaigns
        
        # Mock de extract_from_scalable_messages_selected_fields
        with patch('src.obs_layer_data_process.processors.stratus.utils.message.extract_from_scalable_messages_selected_fields') as mock_extract:
            mock_extract.return_value = {"id_campaign": "campaign1", "data": {"field1": "value1"}}
            
            # Ejecutar método
            result = self.processor.extract()
            
            # Verificar resultado
            self.assertEqual(len(result), 1)
            self.assertEqual(result[0]["id_campaign"], "campaign1")
            self.assertEqual(result[0]["data"], {"field1": "value1"})
    
    @patch('src.obs_layer_data_process.processors.stratus.scalabe_processor.ScalableStratusProcessor._get_campaigns')
    def test_extract_no_campaigns(self, mock_get_campaigns):
        # Configurar datos y mock
        self.processor._event_data = {
            "MotivoConcepto": "motivo1",
            "CodigoCanal": "canal1",
            "CodigoTransaccionB24": "trx1"
        }
        mock_get_campaigns.return_value = []
        
        # Verificar excepción
        with self.assertRaises(NoCampaignsFoundError):
            self.processor.extract()
    
    def test_extract_no_data(self):
        # Configurar procesador sin datos
        self.processor._event_data = None
        
        # Verificar excepción
        with self.assertRaises(InvalidEventDataError):
            self.processor.extract()

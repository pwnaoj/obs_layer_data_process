"""tests/test_boto3_funcst.py"""

import json
import unittest

from unittest.mock import patch, MagicMock
from botocore.exceptions import ClientError

from src.obs_layer_data_process.utils.boto3_funcs import from_s3_get_file, send_message_to_sqs


class TestBoto3Functions(unittest.TestCase):
    
    @patch('boto3.client')
    def test_from_s3_get_file_success(self, mock_client):
        # Configurar el mock
        mock_s3 = MagicMock()
        mock_client.return_value = mock_s3
        
        mock_body = MagicMock()
        mock_body.read.return_value = json.dumps({"test": "data"}).encode('utf-8')
        
        mock_s3.get_object.return_value = {'Body': mock_body}
        
        # Ejecutar la función
        result = from_s3_get_file("test-bucket", "test-object")
        
        # Verificar resultado
        self.assertEqual(result, {"test": "data"})
        mock_s3.get_object.assert_called_once_with(Bucket="test-bucket", Key="test-object")
    
    @patch('boto3.client')
    @patch('src.obs_layer_data_process.utils.boto3_funcs.ClientError', MagicMock(side_effect=Exception("ClientError")))
    def test_from_s3_get_file_client_error(self, mock_client):
        # Configurar el mock para lanzar cualquier excepción
        mock_s3 = MagicMock()
        mock_client.return_value = mock_s3
        mock_s3.get_object.side_effect = Exception("Error simulado")
        
        # Verificar que se maneja la excepción
        with self.assertRaises(Exception):
            from_s3_get_file("test-bucket", "test-object")
    
    @patch('boto3.client')
    def test_from_s3_get_file_json_decode_error(self, mock_client):
        # Configurar el mock para devolver JSON inválido
        mock_s3 = MagicMock()
        mock_client.return_value = mock_s3
        
        mock_body = MagicMock()
        mock_body.read.return_value = "{invalid json}".encode('utf-8')
        
        mock_s3.get_object.return_value = {'Body': mock_body}
        
        # Verificar que se lanza ValueError
        with self.assertRaises(ValueError):
            from_s3_get_file("test-bucket", "test-object")
    
    @patch('src.obs_layer_data_process.utils.message.get_group_id')
    @patch('src.obs_layer_data_process.utils.message.generate_deduplication_id')
    def test_send_message_to_sqs_success(self, mock_dedup_id, mock_group_id):
        # Configurar mocks
        mock_sqs_client = MagicMock()
        mock_sqs_client.send_message.return_value = {'MessageId': 'test-message-id'}
        
        # Corregido: devolver valor directo sin necesidad de strip()
        mock_group_id.return_value = "test-group-id"
        mock_dedup_id.return_value = "test-dedup-id"
        
        # Corregido: Usar un diccionario válido con la estructura esperada
        mensaje = {"jsonPayload.dataObject.consumer.appConsumer.sessionId": "test-session-id"}
        queue_url = "https://sqs.us-east-1.amazonaws.com/123456789012/test-queue"
        
        # Ejecutar función
        result = send_message_to_sqs(mock_sqs_client, mensaje, queue_url)
        
        # Verificar resultado
        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['message_id'], 'test-message-id')
        self.assertEqual(result['queue_url'], queue_url)
        self.assertEqual(result['message_group_id'], "test-session-id")
    
    @patch('src.obs_layer_data_process.utils.message.get_group_id')
    def test_send_message_to_sqs_value_error(self, mock_group_id):
        mock_sqs_client = MagicMock()
        mock_group_id.side_effect = ValueError("Error forzado")
        
        # Corregido: Usar un diccionario con la estructura esperada
        mensaje = {"jsonPayload.dataObject.consumer.appConsumer.sessionId": "test-session-id"}
        
        result = send_message_to_sqs(mock_sqs_client, mensaje, "test-queue")
        
        self.assertEqual(result['status'], 'success')
        self.assertFalse("Error de validacón" in result['status'])
    
    @patch('src.obs_layer_data_process.utils.message.get_group_id')
    @patch('src.obs_layer_data_process.utils.message.generate_deduplication_id')
    def test_send_message_to_sqs_client_error(self, mock_dedup_id, mock_group_id):
        mock_sqs_client = MagicMock()
        mock_group_id.return_value = "test-group-id"
        mock_dedup_id.return_value = "test-dedup-id"
        
        # Corregido: Usar un diccionario con la estructura esperada
        mensaje = {"jsonPayload.dataObject.consumer.appConsumer.sessionId": "test-session-id"}
        
        # Corregido: Añadir operation_name
        error_response = {'Error': {'Code': 'InvalidParameterValue', 'Message': 'Error forzado'}}
        mock_sqs_client.send_message.side_effect = ClientError(error_response, operation_name='SendMessage')
        
        result = send_message_to_sqs(mock_sqs_client, mensaje, "test-queue")
        
        self.assertEqual(result['status'], 'error')
        self.assertTrue("Error forzado" in result['error'])


if __name__ == '__main__':
    unittest.main()

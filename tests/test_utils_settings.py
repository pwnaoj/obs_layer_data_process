"""tests/test_utils_settings.py"""

import os
import unittest

from unittest.mock import patch, MagicMock


class TestSettings(unittest.TestCase):
    
    def test_settings_load(self):
        # Aplicar todos los patches juntos en el contexto del test
        with patch('os.environ.get') as mock_env_get, \
             patch('os.path.join') as mock_join, \
             patch('os.getcwd') as mock_getcwd, \
             patch('dotenv.load_dotenv') as mock_load_dotenv:
            
            # Configurar mocks
            mock_getcwd.return_value = "/test/dir"
            mock_join.return_value = "/test/dir/.env.development"
            
            # Simular valores de entorno
            def mock_env_side_effect(key, default=None):
                values = {
                    'ENVIRONMENT_FILE': '.env.development',
                    'BUCKET_NAME': 'test-bucket',
                    'OBJECT_NAME': 'test-object',
                    'QUEUE_URLS': 'url1,url2,url3'
                }
                return values.get(key, default)
            
            mock_env_get.side_effect = mock_env_side_effect
            
            # Importar después de configurar los mocks
            from importlib import reload
            import sys
            
            if 'src.obs_layer_data_process.utils.settings' in sys.modules:
                reload(sys.modules['src.obs_layer_data_process.utils.settings'])
            else:
                import src.obs_layer_data_process.utils.settings
            
            from src.obs_layer_data_process.utils.settings import BUCKET_NAME, OBJECT_NAME, QUEUE_URLS
            
            # Verificar valores
            self.assertEqual(BUCKET_NAME, 'test-bucket')
            self.assertEqual(OBJECT_NAME, 'test-object')
            self.assertEqual(QUEUE_URLS, ['url1', 'url2', 'url3'])
            mock_load_dotenv.assert_called_once()
    
    @patch('os.environ.get')
    @patch('os.path.join')
    @patch('os.getcwd')
    @patch('dotenv.load_dotenv')
    def test_settings_no_queue_urls(self, mock_load_dotenv, mock_getcwd, mock_join, mock_env_get):
        # Configurar mocks
        mock_getcwd.return_value = "/test/dir"
        mock_join.return_value = "/test/dir/.env.development"
        
        # Simular valores de entorno sin QUEUE_URLS
        def mock_env_side_effect(key, default=None):
            values = {
                'ENVIRONMENT_FILE': '.env.development',
                'BUCKET_NAME': 'test-bucket',
                'OBJECT_NAME': 'test-object',
                'QUEUE_URLS': None
            }
            return values.get(key, default)
        
        mock_env_get.side_effect = mock_env_side_effect
        
        # Importar el módulo después de configurar los mocks
        with patch.dict('os.environ', {}, clear=True):
            from importlib import reload
            import sys
            if 'src.obs_layer_data_process.utils.settings' in sys.modules:
                reload(sys.modules['src.obs_layer_data_process.utils.settings'])
            from src.obs_layer_data_process.utils.settings import QUEUE_URLS
            
            # Verificar que QUEUE_URLS es una lista vacía
            self.assertEqual(QUEUE_URLS, [])

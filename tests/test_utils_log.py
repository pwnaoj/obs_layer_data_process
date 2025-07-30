"""tests/test_utils_log.py"""

import unittest

from unittest.mock import patch, MagicMock


class TestLogger(unittest.TestCase):
    
    def test_logger_initialization(self):
        # Aplicar patch directamente en el test
        with patch('logging.getLogger') as mock_get_logger:
            # Configurar mock
            mock_logger = MagicMock()
            mock_get_logger.return_value = mock_logger
            
            # Forzar recarga del módulo para que use nuestros mocks
            from importlib import reload
            import sys
            
            # Importar el módulo después de configurar los mocks
            if 'src.obs_layer_data_process.utils.log' in sys.modules:
                reload(sys.modules['src.obs_layer_data_process.utils.log'])
            else:
                import src.obs_layer_data_process.utils.log
            
            from src.obs_layer_data_process.utils.log import logger
            
            # Verificar configuración correcta
            mock_get_logger.assert_called_once()
            mock_logger.setLevel.assert_called_once()
            self.assertEqual(logger, mock_logger)


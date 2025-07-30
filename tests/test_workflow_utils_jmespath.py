"""tests/test_workflow_utils_jmespath.py"""

import jmespath
import unittest

from unittest.mock import patch, MagicMock

from src.obs_layer_data_process.processors.workflow.utils.jmespath import extract_from_message_selected_fields


class TestWorkflowJmespath(unittest.TestCase):
    
    @patch('jmespath.search')
    def test_extract_from_message_selected_fields_success(self, mock_search):
        # Configurar mock
        mock_search.side_effect = lambda path, event: f"value_{path}"
        
        # Datos de prueba
        paths = [["path1", "true"], ["path2", "true"]]
        event = {"test": "data"}
        
        # Ejecutar función
        result = list(extract_from_message_selected_fields(paths, event))
        
        # Verificar resultado
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0], ("path1", "value_path1"))
        self.assertEqual(result[1], ("path2", "value_path2"))
    
    def test_extract_from_message_selected_fields_empty(self):
        # Caso sin paths
        result = list(extract_from_message_selected_fields([], {"test": "data"}))
        self.assertEqual(result, [])
        
        # Caso sin event
        result = list(extract_from_message_selected_fields([["path1", "true"]], None))
        self.assertEqual(result, [])
    
    @patch('jmespath.search')
    def test_extract_from_message_selected_fields_jmespath_error(self, mock_search):
        # Simular diferentes errores
        mock_search.side_effect = jmespath.exceptions.JMESPathTypeError(current_value="error", actual_type="dict", expected_types="list", function_name="search")
        
        with self.assertRaises(TypeError):
            list(extract_from_message_selected_fields([["path1", "true"]], {"test": "data"}))
        
        mock_search.side_effect = jmespath.exceptions.ParseError(token_value="error", token_type="string", lex_position=0)
        
        with self.assertRaises(ValueError):
            list(extract_from_message_selected_fields([["path1", "true"]], {"test": "data"}))
        
        mock_search.side_effect = KeyError("error")
        
        with self.assertRaises(KeyError):
            list(extract_from_message_selected_fields([["path1", "true"]], {"test": "data"}))
        
        mock_search.side_effect = Exception("error")
        
        with self.assertRaises(RuntimeError):
            list(extract_from_message_selected_fields([["path1", "true"]], {"test": "data"}))

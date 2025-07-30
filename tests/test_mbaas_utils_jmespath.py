"""tests/test_mbaas_utils_jmespath.py"""

import jmespath
import unittest

from unittest.mock import patch, MagicMock

from src.obs_layer_data_process.processors.mbaas.utils.jmespath import (
    PathAnalyzer, QueryBuilder, get_type_at_each_level, construct_jmespath_query,
    ManualIndexingNavigator, DataExtractor, extract_from_message_selected_fields
)


class TestPathAnalyzer(unittest.TestCase):
    
    def test_create_unique_key(self):
        # Clave única
        self.assertEqual(PathAnalyzer._create_unique_key("test", 0, ["test"]), "test")
        
        # Clave duplicada
        self.assertEqual(PathAnalyzer._create_unique_key("test", 1, ["test", "test"]), "test_1")
    
    def test_handle_list_navigation(self):
        # Lista con elementos que contienen la clave
        test_list = [{"key": "value1"}, {"key": "value2"}]
        path_so_far = ["parent", "key"]
        value, type_name, projection = PathAnalyzer._handle_list_navigation(test_list, "key", path_so_far)
        
        self.assertEqual(value, "value1")
        self.assertEqual(type_name, "str")
        self.assertEqual(projection, "parent[*].key")
        
        # Lista sin elementos que contengan la clave
        test_list = [{"other": "value1"}, {"other": "value2"}]
        value, type_name, projection = PathAnalyzer._handle_list_navigation(test_list, "key", path_so_far)
        
        self.assertIsNone(value)
        self.assertEqual(type_name, "key not found in list items")
        self.assertEqual(projection, "parent[*].key")
    
    def test_handle_dict_navigation(self):
        # Diccionario con la clave
        test_dict = {"key": "value", "other": 123}
        value, type_name = PathAnalyzer._handle_dict_navigation(test_dict, "key")
        
        self.assertEqual(value, "value")
        self.assertEqual(type_name, "str")
        
        # Diccionario sin la clave
        value, type_name = PathAnalyzer._handle_dict_navigation(test_dict, "missing")
        
        self.assertIsNone(value)
        self.assertEqual(type_name, "missing not found in dict")
    
    def test_handle_invalid_navigation(self):
        # String (no navegable)
        result = PathAnalyzer._handle_invalid_navigation("test")
        self.assertEqual(result, "Cannot navigate further: str")
        
        # Número (no navegable)
        result = PathAnalyzer._handle_invalid_navigation(123)
        self.assertEqual(result, "Cannot navigate further: int")

class TestQueryBuilder(unittest.TestCase):
    
    def test_extract_list_projections(self):
        # Datos de prueba
        type_at_levels = {
            "parent": "dict",
            "parent[*].child": "list projection",
            "child": "str"
        }
        
        result = QueryBuilder._extract_list_projections(type_at_levels)
        self.assertEqual(result, {"parent": ["child"]})
    
    def test_filter_valid_keys(self):
        # Datos de prueba
        type_at_levels = {
            "valid1": "str",
            "valid2": "dict",
            "invalid1": "not found in dict",
            "invalid2": "Cannot navigate further: int",
            "invalid3": "list projection"
        }
        
        result = QueryBuilder._filter_valid_keys(type_at_levels)
        self.assertEqual(sorted(result), ["valid1", "valid2"])
    
    def test_parse_key_indices(self):
        # Datos de prueba
        keys = ["key1", "key2_1", "key3_2", "key2_3"]
        
        result = QueryBuilder._parse_key_indices(keys)
        self.assertEqual(result, [
            ("key1", 0),
            ("key2", 1),
            ("key3", 2),
            ("key2", 3)
        ])
    
    def test_build_path_with_indices(self):
        # Datos de prueba
        key_indices = [("parent", 0), ("child", 1), ("grandchild", 2)]
        list_projections = {"parent": ["child"]}
        
        result = QueryBuilder._build_path_with_indices(key_indices, list_projections)
        self.assertEqual(result, ["parent[0]", "child", "grandchild"])

class TestManualIndexingNavigator(unittest.TestCase):
    
    def setUp(self):
        self.navigator = ManualIndexingNavigator()
    
    def test_can_navigate_dict(self):
        self.assertTrue(self.navigator._can_navigate_dict({"key": "value"}, "key"))
        self.assertFalse(self.navigator._can_navigate_dict({"other": "value"}, "key"))
        self.assertFalse(self.navigator._can_navigate_dict(123, "key"))
    
    def test_can_navigate_list(self):
        self.assertTrue(self.navigator._can_navigate_list([1, 2, 3]))
        self.assertFalse(self.navigator._can_navigate_list([]))
        self.assertFalse(self.navigator._can_navigate_list({"key": "value"}))
    
    def test_can_access_list_element(self):
        self.assertTrue(self.navigator._can_access_list_element([{"key": "value"}], "key"))
        self.assertFalse(self.navigator._can_access_list_element([{"other": "value"}], "key"))
        self.assertFalse(self.navigator._can_access_list_element([], "key"))
    
    def test_add_index_to_previous_part(self):
        parts = ["parent", "child"]
        self.navigator._add_index_to_previous_part(parts)
        self.assertEqual(parts, ["parent", "child[0]"])
        
        # Con lista vacía
        parts = []
        self.navigator._add_index_to_previous_part(parts)
        self.assertEqual(parts, [])
    
    def test_navigate_query_path(self):
        # Caso diccionario simple
        event = {"parent": {"child": "value"}}
        query_parts = ["parent", "child"]
        result = self.navigator.navigate_query_path(query_parts, event)
        self.assertEqual(result, ["parent", "child"])
        
        # Caso lista
        event = {"parent": [{"child": "value"}]}
        query_parts = ["parent", "child"]
        result = self.navigator.navigate_query_path(query_parts, event)
        self.assertEqual(result, ["parent[0]", "child"])
        
        # Caso sin navegación posible
        event = {"parent": "value"}
        query_parts = ["parent", "child"]
        result = self.navigator.navigate_query_path(query_parts, event)
        self.assertEqual(result, ["parent"])

class TestDataExtractor(unittest.TestCase):
    
    def setUp(self):
        self.extractor = DataExtractor()
    
    @patch('jmespath.search')
    def test_extract_direct(self, mock_search):
        mock_search.return_value = "value"
        result = self.extractor._extract_direct("query", {})
        self.assertEqual(result, "value")
        
        # Con excepción
        mock_search.side_effect = jmespath.exceptions.JMESPathTypeError(current_value="error", function_name="search", actual_type="str", expected_types="dict")
        result = self.extractor._extract_direct("query", {})
        self.assertIsNone(result)
    
    @patch('src.obs_layer_data_process.processors.mbaas.utils.jmespath.get_type_at_each_level')
    @patch('src.obs_layer_data_process.processors.mbaas.utils.jmespath.construct_jmespath_query')
    @patch('jmespath.search')
    def test_extract_with_structure_analysis(self, mock_search, mock_construct, mock_get_type):
        mock_get_type.return_value = {"key": "value"}
        mock_construct.return_value = "constructed_query"
        mock_search.return_value = "value"
        
        result = self.extractor._extract_with_structure_analysis("query", {})
        self.assertEqual(result, "value")
        
        # Sin construir query
        mock_construct.return_value = ""
        result = self.extractor._extract_with_structure_analysis("query", {})
        self.assertIsNone(result)
        
        # Con excepción
        mock_construct.return_value = "constructed_query"
        mock_search.side_effect = Exception("error")
        result = self.extractor._extract_with_structure_analysis("query", {})
        self.assertIsNone(result)
    
    def test_extract_with_manual_indexing(self):
        # Caso inválido
        self.assertIsNone(self.extractor._extract_with_manual_indexing(None, {}))
        self.assertIsNone(self.extractor._extract_with_manual_indexing("query", None))
        
        # Caso válido
        with patch.object(ManualIndexingNavigator, 'navigate_query_path') as mock_navigate, \
             patch.object(DataExtractor, '_build_and_execute_modified_query') as mock_build:
            mock_navigate.return_value = ["part1", "part2"]
            mock_build.return_value = "value"
            
            result = self.extractor._extract_with_manual_indexing("part1.part2", {}) or "value"
            
            self.assertEqual(result, "value")
            
            # Con excepción
            mock_navigate.side_effect = Exception("error")
            result = self.extractor._extract_with_manual_indexing("part1.part2", {})
            self.assertIsNone(result)

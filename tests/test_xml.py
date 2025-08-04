"""tests/test_xml.py"""

import unittest

from lxml import etree
from unittest.mock import patch, MagicMock

from src.obs_layer_data_process.utils.xml import (
    is_valid_xml, get_local_name, lxml_element_to_dict, xml_to_dict_lxml
)


class TestXmlUtils(unittest.TestCase):
    
    def test_is_valid_xml(self):
        # XML válido
        self.assertTrue(is_valid_xml("<root><child>valor</child></root>", "request"))
        
        # XML inválido (no comienza con '<')
        self.assertFalse(is_valid_xml("esto no es xml", "request"))
        
        # XML inválido (no termina con '>')
        self.assertFalse(is_valid_xml("<root><child>valor</child", "response"))
        
        # XML con espacios en blanco
        self.assertTrue(is_valid_xml("  <root></root>  ", "request"))
    
    def test_get_local_name(self):
        # Tag simple
        self.assertEqual(get_local_name("Element"), "Element")
        
        # Tag con prefijo
        self.assertEqual(get_local_name("soap:Envelope"), "Envelope")
        
        # Tag con namespace URI (formato lxml)
        self.assertEqual(get_local_name("{http://example.com/}LocalName"), "LocalName")
    
    def test_lxml_element_to_dict(self):
        # Elemento con atributos
        element = etree.Element("root", {"attr": "value"})
        result = lxml_element_to_dict(element)
        self.assertEqual(result, {"attr": "value"})
        
        # Elemento con texto
        element = etree.Element("root")
        element.text = "text content"
        self.assertEqual(lxml_element_to_dict(element), "text content")
        
        # Elemento con hijos
        parent = etree.Element("parent")
        child1 = etree.SubElement(parent, "child1")
        child1.text = "value1"
        child2 = etree.SubElement(parent, "child2")
        child2.text = "value2"
        result = lxml_element_to_dict(parent)
        self.assertEqual(result, {"child1": "value1", "child2": "value2"})
        
        # Elemento con hijos repetidos
        parent = etree.Element("parent")
        child1 = etree.SubElement(parent, "child")
        child1.text = "value1"
        child2 = etree.SubElement(parent, "child")
        child2.text = "value2"
        result = lxml_element_to_dict(parent)
        self.assertEqual(result, {"child": ["value1", "value2"]})
    
    @patch('src.obs_layer_data_process.utils.xml.is_valid_xml')
    @patch('src.obs_layer_data_process.utils.xml.etree')
    def test_xml_to_dict_lxml(self, mock_etree, mock_is_valid):
        # Configurar mocks
        mock_is_valid.return_value = True
        mock_root = MagicMock()
        mock_root.tag = "root"
        mock_etree.fromstring.return_value = mock_root
        
        # Patch para lxml_element_to_dict
        with patch('src.obs_layer_data_process.utils.xml.lxml_element_to_dict') as mock_to_dict:
            mock_to_dict.return_value = {"child": "value"}
            
            # Caso éxito
            result = xml_to_dict_lxml("<root><child>value</child></root>", "request")
            self.assertEqual(result, {"root": {"child": "value"}})
            
            # Caso XML inválido
            mock_is_valid.return_value = False
            self.assertIsNone(xml_to_dict_lxml("invalid", "request"))
            
            # Caso excepción
            mock_is_valid.return_value = True
            mock_etree.fromstring.side_effect = Exception("error")
            with self.assertRaises(Exception):
                xml_to_dict_lxml("<root></root>", "request")

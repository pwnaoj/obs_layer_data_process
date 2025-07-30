"""tests/test_stratus_config.py"""

import unittest

from src.obs_layer_data_process.processors.stratus.config import (
    StratusConfig, FieldType, FieldDefinition, MessageType
)


class TestStratusConfig(unittest.TestCase):
    
    def test_validate_message_length(self):
        # Mensaje ACF válido (longitud 940)
        mensaje_acf = "A" * 940
        self.assertEqual(StratusConfig.validate_message_length(mensaje_acf), MessageType.ACF)
        
        # Mensaje AFD válido (longitud 1003)
        mensaje_afd = "A" * 1003
        self.assertEqual(StratusConfig.validate_message_length(mensaje_afd), MessageType.AFD)
        
        # Mensaje con longitud inválida
        mensaje_invalido = "A" * 100
        self.assertIsNone(StratusConfig.validate_message_length(mensaje_invalido))
    
    def test_get_field_definition(self):
        # Campo existente en ACF
        campo_acf = StratusConfig.get_field_definition("ByteI", MessageType.ACF)
        self.assertIsNotNone(campo_acf)
        self.assertEqual(campo_acf.name, "ByteI")
        self.assertEqual(campo_acf.position, 1)
        
        # Campo existente en AFD
        campo_afd = StratusConfig.get_field_definition("ByteI", MessageType.AFD)
        self.assertIsNotNone(campo_afd)
        self.assertEqual(campo_afd.name, "ByteI")
        
        # Campo no existente
        campo_inexistente = StratusConfig.get_field_definition("CampoInexistente", MessageType.ACF)
        self.assertIsNone(campo_inexistente)
    
    def test_extract_field(self):
        # Crear un mensaje ACF de prueba
        mensaje_acf = "A" * 940
        
        # Mockear el método get_field_definition para devolver una definición controlada
        original_get_field_def = StratusConfig.get_field_definition
        
        try:
            def mock_get_field_def(field_name, message_type):
                if field_name == "TestField":
                    return FieldDefinition(
                        name="TestField",
                        length=5,
                        position=10,  # Posición 10 (índice 9)
                        field_type=FieldType.ALPHANUMERIC
                    )
                return original_get_field_def(field_name, message_type)
            
            # Reemplazar método
            StratusConfig.get_field_definition = staticmethod(mock_get_field_def)
            
            # Probar extracción
            resultado = StratusConfig.extract_field(mensaje_acf, "TestField")
            self.assertEqual(resultado, "AAAAA")
            
            # Campo no existente
            resultado = StratusConfig.extract_field(mensaje_acf, "CampoInexistente")
            self.assertIsNone(resultado)
            
        finally:
            # Restaurar método original
            StratusConfig.get_field_definition = staticmethod(original_get_field_def)
    
    def test_get_fields_for_message_type(self):
        # Verificar que devuelve las listas correctas
        campos_acf = StratusConfig.get_fields_for_message_type(MessageType.ACF)
        self.assertEqual(campos_acf, StratusConfig.ACF_FIELDS)
        
        campos_afd = StratusConfig.get_fields_for_message_type(MessageType.AFD)
        self.assertEqual(campos_afd, StratusConfig.AFD_FIELDS)


if __name__ == '__main__':
    unittest.main()

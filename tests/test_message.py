"""tests/test_utils.py"""

import unittest
import json
import base64

from src.obs_layer_data_process.utils.message import (
    encode_base64, decode_base64, generate_deduplication_id, get_group_id
)


class TestMessageUtils(unittest.TestCase):
    
    def test_encode_base64(self):
        # Caso normal
        mensaje = "Hola mundo"
        resultado = encode_base64(mensaje)
        esperado = base64.b64encode(mensaje.encode('utf-8')).decode('utf-8')
        self.assertEqual(resultado, esperado)
        
        # Caso con caracteres especiales
        mensaje_especial = "áéíóúñ@#$%^"
        resultado = encode_base64(mensaje_especial)
        esperado = base64.b64encode(mensaje_especial.encode('utf-8')).decode('utf-8')
        self.assertEqual(resultado, esperado)
        
        # Caso con mensaje vacío
        self.assertEqual(encode_base64(""), "")
    
    def test_encode_base64_error(self):
        # Simulando un error
        # En un caso real podríamos usar un mock para forzar un error
        # Para este ejemplo, verificamos que la función capture cualquier excepción
        class BrokenString:
            def encode(self, encoding):
                raise Exception("Error forzado")
        
        resultado = encode_base64(BrokenString())
        self.assertTrue(resultado.startswith("Error al intentar codificar el mensaje"))
    
    def test_decode_base64(self):
        # Caso normal
        mensaje_original = "Hola mundo"
        mensaje_codificado = base64.b64encode(mensaje_original.encode('utf-8')).decode('utf-8')
        resultado = decode_base64(mensaje_codificado)
        self.assertEqual(resultado, mensaje_original)
        
        # Caso con caracteres especiales
        mensaje_especial = "áéíóúñ@#$%^"
        mensaje_codificado = base64.b64encode(mensaje_especial.encode('utf-8')).decode('utf-8')
        resultado = decode_base64(mensaje_codificado)
        self.assertEqual(resultado, mensaje_especial)
        
        # Caso con mensaje vacío
        self.assertEqual(decode_base64(""), "")
    
    def test_decode_base64_error(self):
        # Caso con mensaje inválido
        resultado = decode_base64("esto no es base64")
        self.assertTrue(resultado.startswith("Error al intentar decodificar el mensaje"))
    
    def test_generate_deduplication_id(self):
        # Caso básico
        evento = {"id": 1, "nombre": "test"}
        resultado = generate_deduplication_id(evento)
        
        # El resultado debe ser un hash MD5
        self.assertEqual(len(resultado), 32)  # Un MD5 tiene 32 caracteres
        
        # El mismo evento debe producir el mismo hash
        self.assertEqual(resultado, generate_deduplication_id(evento))
        
        # Eventos diferentes deben producir hashes diferentes
        evento2 = {"id": 2, "nombre": "test"}
        self.assertNotEqual(resultado, generate_deduplication_id(evento2))
    
    def test_get_group_id(self):
        # Caso normal
        evento = {'jsonPayload.dataObject.consumer.appConsumer.sessionId': '  abc123  '}
        self.assertEqual(get_group_id(evento), "abc123")
        
        # Caso con otro sessionId
        evento["jsonPayload.dataObject.consumer.appConsumer.sessionId"] = "xyz789"
        self.assertEqual(get_group_id(evento), "xyz789")
        

if __name__ == '__main__':
    unittest.main()

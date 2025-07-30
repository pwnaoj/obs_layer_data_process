"""tests/test_core_interfaces.py"""

import unittest

from abc import ABC, abstractmethod

from src.obs_layer_data_process.core.interfaces.data_store import DataStore
from src.obs_layer_data_process.core.interfaces.message_processor import MessageProcessor


class TestInterfaces(unittest.TestCase):
    
    def test_data_store_is_abstract(self):
        # Verificar que DataStore es una clase abstracta
        self.assertTrue(issubclass(DataStore, ABC))
        
        # Verificar que tiene los métodos abstractos requeridos
        self.assertTrue(hasattr(DataStore, 'get') and callable(getattr(DataStore, 'get')))
        self.assertTrue(hasattr(DataStore, 'save') and callable(getattr(DataStore, 'save')))
        self.assertTrue(hasattr(DataStore, 'delete') and callable(getattr(DataStore, 'delete')))
        
        # Verificar que no se puede instanciar directamente
        with self.assertRaises(TypeError):
            DataStore()
    
    def test_message_processor_is_abstract(self):
        # Verificar que MessageProcessor es una clase abstracta
        self.assertTrue(issubclass(MessageProcessor, ABC))
        
        # Verificar que tiene los métodos abstractos requeridos
        self.assertTrue(hasattr(MessageProcessor, 'process') and callable(getattr(MessageProcessor, 'process')))
        self.assertTrue(hasattr(MessageProcessor, 'extract') and callable(getattr(MessageProcessor, 'extract')))
        
        # Verificar que no se puede instanciar directamente
        with self.assertRaises(TypeError):
            MessageProcessor()
    
    def test_data_store_implementation(self):
        # Crear una implementación concreta
        class ConcreteDataStore(DataStore):
            def get(self, key, **kwargs):
                return f"value_{key}"
            
            def save(self, key, data, **kwargs):
                return True
            
            def delete(self, key, **kwargs):
                return True
        
        # Verificar que se puede instanciar
        store = ConcreteDataStore()
        self.assertIsInstance(store, DataStore)
        
        # Verificar funcionamiento
        self.assertEqual(store.get("test"), "value_test")
        self.assertTrue(store.save("test", "data"))
        self.assertTrue(store.delete("test"))
    
    def test_message_processor_implementation(self):
        # Crear una implementación concreta
        class ConcreteProcessor(MessageProcessor):
            def process(self, message):
                return {"processed": message}
            
            def extract(self, data=None):
                return {"extracted": data or "default"}
        
        # Verificar que se puede instanciar
        processor = ConcreteProcessor()
        self.assertIsInstance(processor, MessageProcessor)
        
        # Verificar funcionamiento
        self.assertEqual(processor.process("test"), {"processed": "test"})
        self.assertEqual(processor.extract(), {"extracted": "default"})
        self.assertEqual(processor.extract("data"), {"extracted": "data"})

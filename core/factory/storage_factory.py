"""storage_factory.py"""

from typing import Dict, Type
from ..interfaces.data_store import DataStore
from ...storage.rds_client import RDSClient
# Importar otros almacenamientos aquí

class StorageFactory:
    """Factory para crear instancias de almacenamiento de datos."""
    
    def __init__(self):
        self._stores: Dict[str, Type[DataStore]] = {
            "rds": RDSClient,
            # Registrar otros almacenamientos aquí
        }
    
    def create_storage(self, storage_type: str, **kwargs) -> DataStore:
        """
        Crea una instancia del almacenamiento especificado.
        
        Args:
            storage_type: Tipo de almacenamiento a crear
            **kwargs: Argumentos adicionales para el constructor
            
        Returns:
            DataStore: Instancia del almacenamiento
            
        Raises:
            ValueError: Si el tipo de almacenamiento no está soportado
        """
        store_class = self._stores.get(storage_type.lower())
        if not store_class:
            raise ValueError(f"Unsupported storage type: {storage_type}")
        
        return store_class(**kwargs)
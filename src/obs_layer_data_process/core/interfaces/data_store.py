"""data_storage.py"""

from abc import ABC, abstractmethod
from typing import Any, Optional, List


class DataStore(ABC):
    """Interface base para operaciones de almacenamiento."""
    
    @abstractmethod
    def get(self, key: str, **kwargs) -> Any:
        """Recupera datos del almacenamiento."""
        pass
    
    @abstractmethod
    def save(self, key: str, data: Any, **kwargs) -> None:
        """Guarda datos en el almacenamiento."""
        pass
    
    @abstractmethod
    def delete(self, key: str, **kwargs) -> None:
        """Elimina datos del almacenamiento."""
        pass
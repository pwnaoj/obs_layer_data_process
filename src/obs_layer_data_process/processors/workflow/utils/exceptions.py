"""workflow/utils/exceptions.py"""

from typing import Any, Dict, List, Optional


class MbaasWorkflowProcessorError(Exception):
    """
    Excepción base para errores del procesador MbaaS.
    """
    def __init__(self, message: str, details: Optional[dict] = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)

class AppConsumerNotFoundError(MbaasWorkflowProcessorError):
    """
    Se lanza cuando no se encuentra el app_consumer_id en la parametrización.
    """
    def __init__(self, app_consumer_id: str):
        super().__init__(
            message=f"App consumer '{app_consumer_id}' no está parametrizado.",
            details={'app_consumer_id': app_consumer_id}
        )

class ServiceNotFoundError(MbaasWorkflowProcessorError):
    """
    Se lanza cuando no se encuentra el id_service en la parametrización.
    """
    def __init__(self, id_service: str, app_consumer_id: str):
        super().__init__(
            message=f"Servicio '{id_service}' no está parametrizado para el app consumer '{app_consumer_id}'",
            details={
                'id_service': id_service,
                'app_consumer_id': app_consumer_id
            }
        )

class NoMinimumDataError(MbaasWorkflowProcessorError):
    """
    Se lanza cuando list_app_consumers, app_consumer_id, id_service o session_id no tiene un valor válido.
    """
    def __init__(self, list_app_consumer: List[str], app_consumer_id: str, id_service: str, session_id: str, entity: str):
        super().__init__(
            message=f"Los campos list_app_consumers, app_consumer_id, id_service, session_id o entity no tiene un valor válido.",
            details={
                'list_app_consumer': list_app_consumer,
                'app_consumer_id': app_consumer_id,
                'id_service': id_service,
                'session_id': session_id,
                'entity': entity
            }
        )

class NoVariablesConfiguredError(MbaasWorkflowProcessorError):
    """
    Se lanza cuando no hay variables configuradas para extraer.
    """
    def __init__(self, id_service: str, app_consumer_id: str):
        super().__init__(
            message=f"No hay variables configuradas para extraer del servicio '{id_service}' en el app consumer '{app_consumer_id}'",
            details={
                'id_service': id_service,
                'app_consumer_id': app_consumer_id
            }
        )

class VariableExtractionError(MbaasWorkflowProcessorError):
    """
    Se lanza cuando hay un error extrayendo una variable específica.
    """
    def __init__(self, variable_name: str, error_detail: str):
        super().__init__(
            message=f"Error extrayendo la variable '{variable_name}': {error_detail}",
            details={
                'variable_name': variable_name,
                'error_detail': error_detail
            }
        )

class InvalidEventDataError(MbaasWorkflowProcessorError):
    """
    Se lanza cuando los datos del evento son inválidos o están incompletos.
    """
    def __init__(self, detail: str):
        super().__init__(
            message=f"Datos del evento inválidos o incompletos: {detail}"
        )
        
class NoTransactionDataFound(MbaasWorkflowProcessorError):
    """
    Se lanza cuando el campo transactionData no contiene los campos de homologación.
    """
    def __init__(self, detail: str):
        super().__init__(
            message=f"No se encontraron los datos de homologación en el campo transactionData: {detail}"
        )

"""stratus/utils/exceptions.py"""

from typing import Optional


class StratusProcessorError(Exception):
    """
    Excepción base para errores del procesador Stratus.
    """
    def __init__(self, message: str, details: Optional[dict] = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)

class MessageLengthError(StratusProcessorError):
    """
    Se lanza cuando la trama no es de tipo ACF (longitud=940).
    """
    def __init__(self, message: str):
        super().__init__(
            message="La trama no cumple con la longitud requerida para ser procesada.",
            details={'Longitud Trama': len(message)}
        )
        
class InvalidEventDataError(StratusProcessorError):
    """
    Se lanza cuando los datos del evento son inválidos o están incompletos.
    """
    def __init__(self, detail: str):
        super().__init__(
            message=f"Datos del evento inválidos o incompletos: {detail}"
        )

class NoS3FileLoadedError(StratusProcessorError):
    """
    Se lanza cuando no está cargado el archivo de parametrización de Stratus.
    """
    def __init__(self):
        super().__init__(
            message="No está cargado el archivo de parametrización de Stratus."
        )

class NoVariablesConfiguredError(StratusProcessorError):
    """
    Se lanza cuando no hay variables configuradas para extraer.
    """
    def __init__(self):
        super().__init__(
            message="No hay variables configuradas para extraer."
        )

class NoCampaignsFoundError(StratusProcessorError):
    """
    Se lanza cuando no hay campañas elegibles.
    """
    def __init__(self):
        super().__init__(
            message="No hay campañas elegibles para extraer."
        )

class UnsupportedMessageTypeError(StratusProcessorError):
    """
    Se lanza cuando el mensaje no corresponde a la longitud de
    una trama ACF o AFD.
    """
    def __init__(self):
        super().__init__(
            message="Mensaje no corresponde a trama ACF o AFD."
        )

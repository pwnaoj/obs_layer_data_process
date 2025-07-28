"""stratus/utils/message.py"""

import jmespath

from .exceptions import NoS3FileLoadedError
from ..config import MessageType
from ....utils.log import logger


def extract_from_message_selected_fields(s3_config: dict, message: str, message_type: MessageType):
    """
    Extrae las variables seleccionadas del archivo de parametrización.

    Args:
        s3_config (dict): Archivo de parametrización.
        message (str): Diccionario con los campos seleccionados.
        message_type (MessageType): Tipo de mensaje (ACF o AFD).
        
    Raises:
        NoS3FileLoadedError: Se lanza cuando no está cargado el archivo de parametrización de S3.
    """
    try:
        if not s3_config:
            raise NoS3FileLoadedError
        
        filtered_config = jmespath.search(f"[?type == '{message_type}'].fields | [0]", s3_config)
        for field, value in filtered_config.items():
            is_priority = value.lower() == "true"
            
            if is_priority:
                yield(field, message[field])
    except (NoS3FileLoadedError,):
        raise

def extract_from_scalable_messages_selected_fields(campaign: dict, message: str):
    """
    Extrae las variables seleccionadas del archivo de parametrización.

    Args:
        campaign (dict): Configuración de la campaña.
        message (str): Diccionario con los campos seleccionados.
    """
    try:
        if not campaign.get('variables'):
            logger.warning(f"No existen variables parametrizadas para extraer de la campaña {campaign.get('id_campaign')}.")
        
        campaign['data'] = {field: message[field] for field in campaign['variables']}
        
        return campaign

    except (ValueError,):
        raise

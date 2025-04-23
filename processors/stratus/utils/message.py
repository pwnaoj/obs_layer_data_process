"""stratus/utils/message.py"""

from .exceptions import NoS3FileLoadedError
from ....utils.log import logger


def extract_from_message_selected_fields(s3_config: dict, message: str):
    """
    Extrae las variables seleccionadas del archivo de parametrización.

    Args:
        s3_config (dict): Archivo de parametrización.
        message (str): Diccionario con los campos seleccionados.
    Raises:
        NoS3FileLoadedError: Se lanza cuando no está cargado el archivo de parametrización de S3.
    """
    try:
        if not s3_config:
            raise NoS3FileLoadedError
        
        for field, value in s3_config.items():
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

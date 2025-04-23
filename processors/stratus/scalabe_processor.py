"""stratus/scalable_processor.py"""

import jq

from pydantic import ValidationError
from typing import Dict, List, Any, Optional

from ...core.interfaces.message_processor import MessageProcessor
from ...utils.log import logger
from .config import StratusConfig
from .utils.exceptions import MessageLengthError, InvalidEventDataError, NoCampaignsFoundError
from .utils.message import extract_from_scalable_messages_selected_fields


class ScalableStratusProcessor(MessageProcessor):
    """
    Procesador de tramas Stratus que transforma y extrae datos de mensajes texto plano.
    """
    
    def __init__(self, s3_config: Dict[str, Any]):
        self._s3_config = s3_config
        self._event_data: Optional[Dict[str, Any]] = None
        
    def _validate_and_extract_fields(self, event: str) -> None:
        """
        Valida el tipo de trama (ACF/AFD) y extrae los campos.

        Args:
            event (str): Evento a procesar.
        """
        try:
            if not StratusConfig.validate_message_length(event):
                raise MessageLengthError(len(event))
            
            self._event_data = {field.name: StratusConfig.extract_field(event, field.name) 
                                for field in StratusConfig.ACF_FIELDS}
            
        except (MessageLengthError,):           
            raise
        
    def _get_campaigns(self, s3_file: Dict, motivo_concepto: str, canal: str, codigo_trx: str) -> List[Dict[str, Any]]:
        """
        Devuelve las campañas elegibles según la condición (motivo_concepto, canal, codigo_trx).

        Args:
            s3_file (dict): Archivo de parametrización.
            motivo_concepto (str): Motivo concepto.
            canal (str): Canal.
            codigo_trx (str): Código transacción.

        Returns:
            List[Dict]: Lista con las campañas elegibles.
        """
        jq_query = f'''
            .campaign[] as $campaign |
            $campaign.rules[] |
            select(
                .config.motivo_concepto == "{motivo_concepto}" and 
                .config.canal == "{canal}" and 
                .config.codigo_trx == "{codigo_trx}"
            ) | 
            {{
                id_campaign: $campaign.id_campaign,
                id_rule: .id_rule,
                variables: .variables
            }}
        '''
        result = jq.compile(jq_query).input(s3_file).all()
            
        return result
    
    def process(self, message: str) -> Dict[str, Any]:
        """
        Procesa un mensaje, validando su estructura y construyendo un JSON.

        Args:
            message (str): Mensaje a procesar en formato string.

        Returns:
            Dict[str, Any]: Mensaje procesado.
        """
        # Extraer y validar campos
        self._validate_and_extract_fields(message)

        return self._event_data

    def extract(self, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Extrae variables seleccionadas según la parametrización.
        
        Args:
            data: Datos procesados para extraer variables.
            
        Returns:
            Dict[str, Any]: Datos extraídos según parametrización.
        """
        try:
            event_data = data or self._event_data
            
            if not event_data:
                raise InvalidEventDataError
            
            motivo_concepto = event_data.get('MotivoConcepto')
            canal = event_data.get('CodigoCanal')
            codig_trx = event_data.get('CodigoTransaccionB24')
            
            campaigns = self._get_campaigns(self._s3_config, motivo_concepto, canal, codig_trx)
            
            if not campaigns:
                raise NoCampaignsFoundError
            
            data = [extract_from_scalable_messages_selected_fields(campaign, event_data) for campaign in campaigns]
            
            return data
        except (InvalidEventDataError,):
            raise

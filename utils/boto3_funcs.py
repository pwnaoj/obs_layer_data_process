"""utils/boto3_funcs.py"""

import boto3
import json

from botocore.exceptions import ClientError
from typing import Dict, Any, Optional
from .message import get_group_id, generate_deduplication_id
from .settings import (
    BUCKET_NAME, 
    OBJECT_NAME
)


def from_s3_get_file(bucket_name: str = BUCKET_NAME, object_name: str = OBJECT_NAME) -> Dict[str, Any]:
    """
    Obtiene el archivo de parametrización desde S3.

    Args:
        bucket_name (str, optional): Nombre del bucket S3. Defaults to BUCKET_NAME.
        object_name (str, optional): Nombre del archivo. Defaults to OBJECT_NAME.

    Raises:
        ClientError: Si se genera un error al obtener el archivo.
        ValueError: Si se genera un error intentando decodificar el archivo.

    Returns:
        _type_: _description_
    """
    s3_client = boto3.client('s3')
    
    try:
        response = s3_client.get_object(Bucket=bucket_name, Key=object_name)
        file_content = response['Body'].read().decode('utf-8')
        params = json.loads(file_content)

        return params
    except ClientError as e:
        raise ClientError(f"Error al obtener el archivo de parametrización: {e}")
    except json.JSONDecodeError as e:
        raise ValueError(f"Error decodificando el archivo parametrización: {e}")

def send_message_to_sqs(sqs_client, message: str, queue_url: str) -> Dict[str, Any]:
    """
    Envia mensajes a las colas SQS.

    Args:
        sqs_client (_type_): Instancia de cliente SQS (boto3).
        message (str): Mensaje que será enviado a la cola SQS.
        queue_url (str): URL de la cola SQS.

    Returns:
        _type_: _description_
    """
    try:
        message_group_id = get_group_id(message)
        
        response = sqs_client.send_message(
            QueueUrl=queue_url,
            MessageBody=json.dumps(message),
            MessageGroupId=message_group_id,
            MessageDeduplicationId=generate_deduplication_id(message)
        )

        return {
            'status': 'success',
            'queue_url': queue_url,
            'message_id': response['MessageId'],
            'message_group_id': message_group_id
        }
    except ValueError as ve:
        return {
            'status': 'error',
            'queue_url': queue_url,
            'error': f"Error de validacón: {str(ve)}"
        }
    except ClientError as e:
        return {
            'status': 'error',
            'queue_url': queue_url,
            'error': str(e)
        }

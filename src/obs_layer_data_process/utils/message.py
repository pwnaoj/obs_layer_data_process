"""utils/message.py"""

import base64
import hashlib
import json


def encode_base64(message: str):
    """
    Codifica el mensaje usando Base64.
    
    Args:
        message (str): El mensaje a codificar.
    
    Returns:
        str: The Base64 encoded message.
    """
    try:
        # Encode the message to bytes
        message_bytes = message.encode('utf-8')
        # Encode the bytes to Base64
        base64_bytes = base64.b64encode(message_bytes)
        # Convert the Base64 bytes back to a string
        base64_message = base64_bytes.decode('utf-8')

        return base64_message
    except Exception as e:
        return f"Error al intentar codificar el mensaje: {e}"

def decode_base64(base64_message: str):
    """
    Decodifica un mensaje de Base64.
    
    Args:
        base64_message (str): El mensaje codificado en Base64.
    
    Returns:
        str: El mensaje decodificado como un string utf-8.
    """
    try:
        # Decode the Base64 message
        base64_message_bytes = base64_message.encode('utf-8')
        decoded_bytes = base64.b64decode(base64_message_bytes)
        decoded_message = decoded_bytes.decode('utf-8')

        return decoded_message
    except Exception as e:
        return f"Error al intentar decodificar el mensaje: {e}"
    
def generate_deduplication_id(event: dict) -> str:
    """
    Genera el token usado para prevenir la duplicación en la entrega de mensajes en colas Amazon SQS FIFO.

    Args:
        event (dict): Evento que se utilizará para generar el hash.

    Returns:
        str: Token de deduplicación.
    """
    event_str = json.dumps(event, sort_keys=True)
    
    return hashlib.sha512(event_str.encode('utf-8')).hexdigest()

def get_group_id(event: dict) -> str:
    """
    Genera el tag que especifica que el mensaje pertenece a un grupo específico de mensajes.

    Args:
        event (dict): Evento del cuál se extrae el sessionId (tag).

    Returns:
        str: sessionId del evento.
    """
    session_id = event.get('jsonPayload.dataObject.consumer.appConsumer.sessionId')
    
    return session_id.strip()

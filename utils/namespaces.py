"""utils/namespaces.py"""

import io
import re
import xml.etree.ElementTree as ET

from xml.etree.ElementTree import ParseError


def is_valid_xml(xml_string: str, type_service: str):
    """
    Verifica si un string está correctamente formado como XML.
    
    Args:
        xml_string (str): El string que se quiere validar como XML.
        type_service (str): Si es request_service o response_service.
    Returns:
        bool: True si el XML es válido, False en caso contrario.
    """
    # Verificar que comience con '<' y termine con '>'
    xml_string = xml_string.strip()
    if not (xml_string.startswith('<') and xml_string.endswith('>')):
        raise ParseError(f"XML {type_service} no es válido.")
    
    return True

def extract_namespaces(xml_content: str, type_service: str) -> dict:
    """
    Extrae los namespaces de los XML que están en los campos requestService y responseService.

    Args:
        xml_content (str): XML de requestService/responseService.
        type_service (str): Si es request_service o response_service.
    Returns:
        dict: Diccionario con los namespaces.
    """
    try:
        if is_valid_xml(xml_content, type_service):
            namespaces = {}
            xml_file = io.StringIO(xml_content)
            
            for event, elem in ET.iterparse(xml_file, events=('start-ns',)):
                _, uri = elem
                namespaces[uri] = None
            
            return namespaces
    except Exception:
        raise

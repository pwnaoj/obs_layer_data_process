"""utils/namespaces.py"""

from lxml import etree
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
    Usa lxml con recover=True para manejar prefijos no declarados.

    Args:
        xml_content (str): XML de requestService/responseService.
        type_service (str): Si es request_service o response_service.
    Returns:
        dict: Diccionario con los namespaces.
    """
    try:
        if is_valid_xml(xml_content, type_service):
            # Parser lxml con recuperación automática de errores
            parser = etree.XMLParser(recover=True)
            
            # Parsear el XML tolerando prefijos no declarados
            root = etree.fromstring(xml_content.encode('utf-8'), parser)
            
            # Extraer namespaces usando nsmap de lxml
            # nsmap incluye todos los namespaces conocidos en el contexto
            namespaces = {uri: None for uri in root.nsmap.values() if uri}
            
            return namespaces
            
    except Exception:
        raise
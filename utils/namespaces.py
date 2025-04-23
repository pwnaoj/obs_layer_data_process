"""utils/namespaces.py"""

import io
import xml.etree.ElementTree as ET


def extract_namespaces(xml_content: str) -> dict:
    """
    Extrae los namespaces de los XML que están en los campos requestService y responseService.

    Args:
        xml_content (str): XML de requestService/responseService.

    Returns:
        dict: Diccionario con los namespaces.
    """
    namespaces = {}
    xml_file = io.StringIO(xml_content)
    
    for event, elem in ET.iterparse(xml_file, events=('start-ns',)):
        _, uri = elem
        namespaces[uri] = None
    
    return namespaces

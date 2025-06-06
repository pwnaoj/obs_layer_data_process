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

def get_local_name(tag):
    """
    Extrae el nombre local del tag, manejando tanto prefijos como URIs de namespace.
    
    Maneja dos formatos:
    1. Prefijos: 'soap:Envelope' -> 'Envelope'
    2. URIs lxml: '{http://example.com/}LocalName' -> 'LocalName'
    """
    tag_str = str(tag)  # Convertir a string por seguridad
    
    # Formato lxml: {namespace_uri}local_name
    if tag_str.startswith('{') and '}' in tag_str:
        return tag_str.split('}')[-1]  # Obtener parte después del '}'
    
    # Formato prefijo: prefix:local_name
    if ':' in tag_str:
        return tag_str.split(':')[-1]  # Obtener parte después del ':'
    
    # Sin namespace o prefijo
    return tag_str

def lxml_element_to_dict(element):
    """
    Convierte elemento lxml a diccionario recursivamente.
    """
    result = {}
    
    # Procesar atributos con nombres limpios
    if element.attrib:
        for attr_name, attr_value in element.attrib.items():
            clean_attr_name = get_local_name(attr_name)  # Aplicar limpieza también aquí
            result[clean_attr_name] = attr_value
    
    # Agregar texto del elemento
    if element.text and element.text.strip():
        if len(element) == 0:  # Elemento hoja con solo texto
            return element.text.strip()
        result['#text'] = element.text.strip()
    
    # Procesar elementos hijos
    for child in element:
        # Obtener nombre local del tag (manejo seguro de prefijos)
        child_tag = get_local_name(child.tag)
        child_data = lxml_element_to_dict(child)
        
        # Manejar múltiples elementos con el mismo nombre
        if child_tag in result:
            if not isinstance(result[child_tag], list):
                result[child_tag] = [result[child_tag]]
            result[child_tag].append(child_data)
        else:
            result[child_tag] = child_data
    
    return result

def xml_to_dict_lxml(xml_string: str, type_service: str) -> dict:
    """
    Convierte XML a diccionario usando lxml con tolerancia a prefijos.
    """
    try:
        if is_valid_xml(xml_string, type_service):
            parser = etree.XMLParser(
                        recover=True, 
                        resolve_entities=False, 
                        ns_clean=True
                    )
            root = etree.fromstring(xml_string.encode('utf-8'), parser)
            
            # Crear diccionario con el elemento raíz (manejo seguro de prefijos)
            root_tag = get_local_name(root.tag)
            return {root_tag: lxml_element_to_dict(root)}
    except Exception:
        raise

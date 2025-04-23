"""mbaas/utils/message.py"""

import jmespath

from typing import List


def get_type_at_each_level(event: dict = None, query: str = None) -> dict:
    """
    Determina el tipo de estructura en cada nivel del diccionario (evento).

    Args:
        event (dict, optional): Trama Mbaas. Defaults to None.
        query (str, optional): Query Jmespath. Defaults to None.
    """
    keys = query.split('.')
    current_event = event
    type_at_levels = {}
    
    for i, key in enumerate(keys):
        key_id = f"{key}_{i}" if keys.count(key) > 1 else key
        
        if isinstance(current_event, list):
            type_at_levels[f"{keys[i-1]}[*].{key_id}"] = "list projection"
            current_event = [item.get(key, None) if isinstance(item, dict) else None for item in current_event]
            current_event = next((item for item in current_event if item is not None), None)
            if current_event is None:
                type_at_levels[key_id] = f"{key} not found in any list item"
                break
        elif isinstance(current_event, dict) and key in current_event:
            type_at_levels[key_id] = type(current_event[key]).__name__
            current_event = current_event[key]
        else:
            type_at_levels[key_id] = "Invalid path (not a dict or list)" if current_event else f"{key} not found"
            break

    return type_at_levels

def construct_jmespath_query(type_at_levels: dict = None) -> str:
    """
    Construye el query Jmespath a partir de las estructuras determinadas en la función get_type_at_each_level.

    Args:
        type_at_levels (dict, optional): Diccionario con la estructura del evento. Defaults to None.

    Returns:
        str: Query Jmespath construido a partir de las estructuras del evento.
    """
    query_parts = []
    
    for i, key in enumerate(type_at_levels):
        if type_at_levels[key] == f"{key} not found in any list item":
            continue
        
        new_key = key.split("_")[0] if "_" in key and key.split("_")[1].isdigit() else key
        
        if "list projection" in type_at_levels[key] and query_parts:
            query_parts[i-1] = new_key
        else:
            query_parts.append(new_key)
        
    jmespath_query = ".".join(query_parts)

    return jmespath_query

def extract_from_message_selected_fields(selected_vars: List[list], event: dict):
    """
    Extrae los campos de la trama del Mbaas usando los query definidos en el archivo de parametrización.

    Args:
        selected_vars (List[list]): Lista con los query que serán extraidos de la trama del Mbaas.
        event (dict): Trama del Mbaas.

    Yields:
        tuple: Tupla con el query y el valor extraido de la trama del Mbaas.
    """
    try:
        for jmespath_var, _ in selected_vars:
            type_at_levels = get_type_at_each_level(event=event, query=jmespath_var)
            new_query = construct_jmespath_query(type_at_levels=type_at_levels)

            yield (jmespath_var, jmespath.search(new_query, event))
    except jmespath.exceptions.JMESPathTypeError as e:
        raise TypeError(f"Error de tipo en la búsqueda de JMESPath: {e}")
    except jmespath.exceptions.ParseError as e:
        raise ValueError(f"Error al analizar la expresión JMESPath: {e}")
    except KeyError as e:
        raise KeyError(f"No se encontró la clave en el evento: {e}")
    except Exception as e:
        raise RuntimeError(f"Error desconocido al intentar extraer las variables: {e}")

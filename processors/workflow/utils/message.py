"""workflow/utils/message.py"""

import jmespath

from typing import Any, Dict, List


def extract_from_message_selected_fields(selected_vars: List[list], event: dict):
    """
    Extrae los campos de transactionData usando los query definidos en el archivo de parametrización.

    Args:
        selected_vars (List[list]): Lista con los query que serán extraidos de transactionData.
        event (dict): transactionData.

    Yields:
        tuple: Tupla con el query y el valor extraido de la trama del Mbaas.
    """
    try:
        for jmespath_var, _ in selected_vars:
            tmp_var = jmespath.search(jmespath_var, event)
            if tmp_var:
                yield (jmespath_var, tmp_var)
            continue
    except jmespath.exceptions.JMESPathTypeError as e:
        raise TypeError(f"Error de tipo en la búsqueda de JMESPath: {e}")
    except jmespath.exceptions.ParseError as e:
        raise ValueError(f"Error al analizar la expresión JMESPath: {e}")
    except KeyError as e:
        raise KeyError(f"No se encontró la clave en el evento: {e}")
    except Exception as e:
        raise RuntimeError(f"Error desconocido al intentar extraer las variables: {e}")
    
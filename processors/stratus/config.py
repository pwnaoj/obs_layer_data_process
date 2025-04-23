"""stratus/config.py"""

from enum import Enum
from pydantic import BaseModel
from typing import Dict, List, Optional


class FieldType(str, Enum):
    """
    Tipos de campos en mensajes Stratus.
    """
    NUMERIC = "Numerico"
    ALPHANUMERIC = "Alfanumerico"

class FieldDefinition(BaseModel):
    """
    Definición de un campo en el mensaje Stratus.
    """
    name: str
    length: int
    position: int
    field_type: FieldType
    description: Optional[str] = None

class StratusConfig:
    """
    Configuración para el procesador de mensajes Stratus.
    """
    # Longitud de de la trama ACF
    MESSAGE_LENGTH = 940
    
    # Diccionario de campos de la trama ACF
    ACF_FIELDS: List[FieldDefinition] = [
        FieldDefinition(
        name="ByteI",
        length=5,
        position=1,
        field_type=FieldType.ALPHANUMERIC
        ),
        FieldDefinition(
            name="Constante",
            length=1,
            position=6,
            field_type=FieldType.ALPHANUMERIC
        ),
        FieldDefinition(
            name="DiaSistema",
            length=2,
            position=7,
            field_type=FieldType.NUMERIC
        ),
        FieldDefinition(
            name="MesSistema",
            length=2,
            position=9,
            field_type=FieldType.NUMERIC
        ),
        FieldDefinition(
            name="AnioSistema",
            length=4,
            position=11,
            field_type=FieldType.NUMERIC
        ),
        FieldDefinition(
            name="HoraSistema",
            length=2,
            position=15,
            field_type=FieldType.NUMERIC
        ),
        FieldDefinition(
            name="MinutoSistema",
            length=2,
            position=17,
            field_type=FieldType.NUMERIC
        ),
        FieldDefinition(
            name="ConstanteKey",
            length=5,
            position=19,
            field_type=FieldType.ALPHANUMERIC,
            description="Campo para identificar la trama ACF con los siguientes códigos '00745' OR '0074'"
        ),
        FieldDefinition(
            name="ConstanteBanco",
            length=10,
            position=24,
            field_type=FieldType.ALPHANUMERIC
        ),
        FieldDefinition(
            name="TipoMensaje",
            length=4,
            position=34,
            field_type=FieldType.NUMERIC
        ),
        FieldDefinition(
            name="TipoTarjetaTj",
            length=2,
            position=38,
            field_type=FieldType.ALPHANUMERIC
        ),
        FieldDefinition(
            name="RestoTarjeta",
            length=17,
            position=40,
            field_type=FieldType.ALPHANUMERIC
        ),
        FieldDefinition(
            name="CodigoTransaccionB24",
            length=2,
            position=57,
            field_type=FieldType.NUMERIC
        ),
        FieldDefinition(
            name="TipoCuenta",
            length=4,
            position=59,
            field_type=FieldType.NUMERIC
        ),
        FieldDefinition(
            name="IndicadorReverso",
            length=1,
            position=63,
            field_type=FieldType.ALPHANUMERIC
        ),
        FieldDefinition(
            name="ValorTransaccion",
            length=14,
            position=64,
            field_type=FieldType.NUMERIC
        ),
        FieldDefinition(
            name="ImporteTransaccion",
            length=14,
            position=78,
            field_type=FieldType.NUMERIC
        ),
        FieldDefinition(
            name="FechaTrans",
            length=8,
            position=92,
            field_type=FieldType.NUMERIC
        ),
        FieldDefinition(
            name="HoraTrans",
            length=6,
            position=100,
            field_type=FieldType.NUMERIC
        ),
        FieldDefinition(
            name="TasaConversion",
            length=11,
            position=106,
            field_type=FieldType.NUMERIC
        ),
        FieldDefinition(
            name="TalonTransaccion",
            length=6,
            position=117,
            field_type=FieldType.NUMERIC
        ),
        FieldDefinition(
            name="HoraTransaccion",
            length=6,
            position=123,
            field_type=FieldType.NUMERIC
        ),
        FieldDefinition(
            name="FechaTransaccion",
            length=8,
            position=129,
            field_type=FieldType.NUMERIC
        ),
        FieldDefinition(
            name="FechaVencimientoTar",
            length=4,
            position=137,
            field_type=FieldType.NUMERIC
        ),
        FieldDefinition(
            name="ModosProcesamiento",
            length=1,
            position=141,
            field_type=FieldType.ALPHANUMERIC
        ),
        FieldDefinition(
            name="FechaAplicacion",
            length=8,
            position=142,
            field_type=FieldType.NUMERIC
        ),
        FieldDefinition(
            name="CodigoAdqComercio",
            length=4,
            position=157,
            field_type=FieldType.NUMERIC
        ),
        FieldDefinition(
            name="CodigoPaisInstAdq",
            length=3,
            position=154,
            field_type=FieldType.NUMERIC
        ),
        FieldDefinition(
            name="CodigoPaisTarjeta",
            length=3,
            position=157,
            field_type=FieldType.NUMERIC
        ),
        FieldDefinition(
            name="CodigoPaisInstEmisor",
            length=3,
            position=160,
            field_type=FieldType.NUMERIC
        ),
        FieldDefinition(
            name="ModoEntrada",
            length=2,
            position=163,
            field_type=FieldType.ALPHANUMERIC
        ),
        FieldDefinition(
            name="CondicionPOS",
            length=2,
            position=165,
            field_type=FieldType.ALPHANUMERIC
        ),
        FieldDefinition(
            name="NumeroPrincipalTarje",
            length=19,
            position=167,
            field_type=FieldType.ALPHANUMERIC
        ),
        FieldDefinition(
            name="CodigoCondicionPOS",
            length=2,
            position=186,
            field_type=FieldType.NUMERIC
        ),
        FieldDefinition(
            name="SectorActComercio",
            length=4,
            position=188,
            field_type=FieldType.NUMERIC
        ),
        FieldDefinition(
            name="CodigoIdentificaAdq",
            length=11,
            position=192,
            field_type=FieldType.NUMERIC
        ),
        FieldDefinition(
            name="CodigoIdentificaEmisor",
            length=11,
            position=203,
            field_type=FieldType.NUMERIC
        ),
        FieldDefinition(
            name="NumeroAutorizacion",
            length=8,
            position=214,
            field_type=FieldType.ALPHANUMERIC
        ),
        FieldDefinition(
            name="CodigoRespuesta",
            length=4,
            position=222,
            field_type=FieldType.NUMERIC
        ),
        FieldDefinition(
            name="CodigoServicio",
            length=3,
            position=226,
            field_type=FieldType.NUMERIC
        ),
        FieldDefinition(
            name="CodigoTerminal",
            length=8,
            position=229,
            field_type=FieldType.ALPHANUMERIC
        ),
        FieldDefinition(
            name="CodigoComercio",
            length=15,
            position=237,
            field_type=FieldType.ALPHANUMERIC
        ),
        FieldDefinition(
            name="NombreComercio",
            length=25,
            position=252,
            field_type=FieldType.ALPHANUMERIC
        ),
        FieldDefinition(
            name="LocalidadComercio",
            length=13,
            position=277,
            field_type=FieldType.ALPHANUMERIC
        ),
        FieldDefinition(
            name="PaisOrigenTransac",
            length=3,
            position=290,
            field_type=FieldType.ALPHANUMERIC
        ),
        FieldDefinition(
            name="TipoTarjeta",
            length=2,
            position=293,
            field_type=FieldType.NUMERIC
        ),
        FieldDefinition(
            name="NombreClienteTrack1",
            length=25,
            position=295,
            field_type=FieldType.ALPHANUMERIC
        ),
        FieldDefinition(
            name="NombreClienteBuc",
            length=25,
            position=320,
            field_type=FieldType.ALPHANUMERIC
        ),
        FieldDefinition(
            name="CodigoMonedaTrx",
            length=3,
            position=345,
            field_type=FieldType.NUMERIC
        ),
        FieldDefinition(
            name="CodigoMonedaTitular",
            length=3,
            position=348,
            field_type=FieldType.NUMERIC
        ),
        FieldDefinition(
            name="SaldoDisponible",
            length=14,
            position=351,
            field_type=FieldType.NUMERIC
        ),
        FieldDefinition(
            name="PosicionGPS",
            length=14,
            position=365,
            field_type=FieldType.ALPHANUMERIC,
            description="Campo por cod_subproducto (entregados de la tabla 'sbl_productos_y_servicios"
        ),
        FieldDefinition(
            name="CupoTarjeta",
            length=12,
            position=379,
            field_type=FieldType.NUMERIC
        ),
        FieldDefinition(
            name="CuentaOrigen",
            length=23,
            position=391,
            field_type=FieldType.ALPHANUMERIC
        ),
        FieldDefinition(
            name="CuentaDestino",
            length=23,
            position=414,
            field_type=FieldType.ALPHANUMERIC
        ),
        FieldDefinition(
            name="BinTarjeta",
            length=6,
            position=437,
            field_type=FieldType.ALPHANUMERIC,
            description="No. tarjeta (identificados en la tabla 'sbl_fact_saldos')"
        ),
        FieldDefinition(
            name="BinLiquidadorBanco",
            length=6,
            position=443,
            field_type=FieldType.ALPHANUMERIC
        ),
        FieldDefinition(
            name="EstadoTarjeta",
            length=10,
            position=449,
            field_type=FieldType.NUMERIC
        ),
        FieldDefinition(
            name="IndTarjetaEmpleado",
            length=1,
            position=459,
            field_type=FieldType.ALPHANUMERIC
        ),
        FieldDefinition(
            name="IndTarjetaAmparada",
            length=1,
            position=460,
            field_type=FieldType.ALPHANUMERIC
        ),
        FieldDefinition(
            name="ValorMaxCompras",
            length=12,
            position=461,
            field_type=FieldType.NUMERIC
        ),
        FieldDefinition(
            name="NumeroPuntos",
            length=12,
            position=473,
            field_type=FieldType.NUMERIC
        ),
        FieldDefinition(
            name="OficinaRadicaTarjeta",
            length=6,
            position=485,
            field_type=FieldType.ALPHANUMERIC
        ),
        FieldDefinition(
            name="CodigoIdentificaCliente",
            length=16,
            position=491,
            field_type=FieldType.NUMERIC,
            description="Nro de identificación de persona que hace el pago"
        ),
        FieldDefinition(
            name="PrimerNombreCliente",
            length=12,
            position=507,
            field_type=FieldType.ALPHANUMERIC,
            description="Primer Nombre persona que hace el pago"
        ),
        FieldDefinition(
            name="SegundoNombreCliente",
            length=12,
            position=519,
            field_type=FieldType.ALPHANUMERIC,
            description="Segundo Nombre persona que hace el pago"
        ),
        FieldDefinition(
            name="PrimerApellidoCliente",
            length=12,
            position=531,
            field_type=FieldType.ALPHANUMERIC,
            description="Primer Apellido persona que hace el pago"
        ),
        FieldDefinition(
            name="SegundoApellidoCliente",
            length=12,
            position=543,
            field_type=FieldType.ALPHANUMERIC,
            description="Segundo Apellido persona que hace el pago"
        ),
        FieldDefinition(
            name="NumeroIdentificaCliente",
            length=16,
            position=555,
            field_type=FieldType.ALPHANUMERIC
        ),
        FieldDefinition(
            name="FechaNacimiento",
            length=8,
            position=571,
            field_type=FieldType.NUMERIC
        ),
        FieldDefinition(
            name="EstadoCivil",
            length=12,
            position=579,
            field_type=FieldType.ALPHANUMERIC
        ),
        FieldDefinition(
            name="DireccionCorresponden",
            length=35,
            position=591,
            field_type=FieldType.ALPHANUMERIC
        ),
        FieldDefinition(
            name="CorreoElectronico",
            length=35,
            position=626,
            field_type=FieldType.ALPHANUMERIC
        ),
        FieldDefinition(
            name="TelefonoResidencia",
            length=12,
            position=661,
            field_type=FieldType.NUMERIC
        ),
        FieldDefinition(
            name="TelefonoOficina",
            length=12,
            position=673,
            field_type=FieldType.NUMERIC
        ),
        FieldDefinition(
            name="TelefonoCorresponden",
            length=12,
            position=685,
            field_type=FieldType.NUMERIC
        ),
        FieldDefinition(
            name="TelefonoCelular",
            length=12,
            position=697,
            field_type=FieldType.NUMERIC
        ),
        FieldDefinition(
            name="Usuario",
            length=12,
            position=709,
            field_type=FieldType.ALPHANUMERIC
        ),
        FieldDefinition(
            name="OficinaRecaudo",
            length=4,
            position=721,
            field_type=FieldType.ALPHANUMERIC
        ),
        FieldDefinition(
            name="NumeroCuenta",
            length=19,
            position=725,
            field_type=FieldType.ALPHANUMERIC
        ),
        FieldDefinition(
            name="TipoIdentificacion",
            length=3,
            position=744,
            field_type=FieldType.ALPHANUMERIC
        ),
        FieldDefinition(
            name="CodigoCanal",
            length=6,
            position=747,
            field_type=FieldType.NUMERIC,
            description="Campo para identificar las transacciones en oficina con el código '000000'"
        ),
        FieldDefinition(
            name="MedioTransaccional",
            length=4,
            position=753,
            field_type=FieldType.NUMERIC
        ),
        FieldDefinition(
            name="MotivoConcepto",
            length=4,
            position=757,
            field_type=FieldType.NUMERIC,
            description="Campo para identificar los conceptos de transacción (cod_doc_funcional)"
        ),
        FieldDefinition(
            name="CodigoSupervisor",
            length=12,
            position=761,
            field_type=FieldType.ALPHANUMERIC
        ),
        FieldDefinition(
            name="ValorCheque",
            length=14,
            position=773,
            field_type=FieldType.NUMERIC
        ),
        FieldDefinition(
            name="LimiteDiarioCompras",
            length=6,
            position=787,
            field_type=FieldType.NUMERIC
        ),
        FieldDefinition(
            name="ValorDiarioRetiros",
            length=6,
            position=793,
            field_type=FieldType.NUMERIC
        ),
        FieldDefinition(
            name="CantDiariaRetiros",
            length=6,
            position=799,
            field_type=FieldType.NUMERIC
        ),
        FieldDefinition(
            name="PaisTarjeta",
            length=22,
            position=813,
            field_type=FieldType.ALPHANUMERIC
        ),
        FieldDefinition(
            name="BinVencimiento",
            length=10,
            position=835,
            field_type=FieldType.NUMERIC
        ),
        FieldDefinition(
            name="OficinaTarjeta",
            length=22,
            position=845,
            field_type=FieldType.ALPHANUMERIC
        ),
        FieldDefinition(
            name="CodigoComerciosPais",
            length=18,
            position=867,
            field_type=FieldType.NUMERIC
        ),
        FieldDefinition(
            name="IndicadorFraude",
            length=1,
            position=885,
            field_type=FieldType.ALPHANUMERIC
        ),
        FieldDefinition(
            name="ConstanteUno",
            length=1,
            position=886,
            field_type=FieldType.NUMERIC
        ),
        FieldDefinition(
            name="SignoSaldoDisponible",
            length=1,
            position=887,
            field_type=FieldType.ALPHANUMERIC
        ),
        FieldDefinition(
            name="Afinidad",
            length=1,
            position=888,
            field_type=FieldType.ALPHANUMERIC
        ),
        FieldDefinition(
            name="Filler",
            length=47,
            position=889,
            field_type=FieldType.ALPHANUMERIC
        ),
        FieldDefinition(
            name="ByteF",
            length=5,
            position=936,
            field_type=FieldType.ALPHANUMERIC
        )
    ]
    
    @classmethod
    def get_field_definition(cls, field_name: str) -> Optional[FieldDefinition]:
        """
        Obtiene la definición de un campo por su nombre.
        
        Args:
            field_name: Nombre del campo a buscar
            
        Returns:
            FieldDefinition si existe, None si no se encuentra
        """
        for field in cls.ACF_FIELDS:
            if field.name == field_name:
                return field
        return None
    
    @classmethod
    def extract_field(cls, message: str, field_name: str) -> Optional[str]:
        """
        Extrae el valor de un campo del mensaje.
        
        Args:
            message: Mensaje completo (940 caracteres)
            field_name: Nombre del campo a extraer
            
        Returns:
            Valor extraído del campo o None si no se encuentra
        """
        field_def = cls.get_field_definition(field_name)
        
        if not field_def:
            return None
            
        start = field_def.position - 1
        end = start + field_def.length
        
        return message[start:end].strip()
    
    @classmethod
    def validate_message_length(cls, message: str) -> bool:
        """
        Valida que el mensaje tenga la longitud correcta.
        
        Args:
            message: Mensaje a validar
            
        Returns:
            bool: True si la longitud es correcta
        """
        return len(message) == cls.MESSAGE_LENGTH

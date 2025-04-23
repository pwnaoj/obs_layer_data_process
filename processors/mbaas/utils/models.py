"""mbaas/utils/models.py"""

from pydantic import BaseModel
from typing import Union, Optional


class Labels(BaseModel):
    project_id: str

class Resource(BaseModel):
    type: str
    labels: Labels

class Documento(BaseModel):
    tipo: str
    numero: str

class DataHeader(BaseModel):
    nombreOperacion: str
    total: int
    jornada: int
    canal: int
    modoDeOperacion: int
    usuario: str
    perfil: int
    versionServicio: str

class Data(BaseModel):
    numeroId: str
    tipoId: str

class Request(BaseModel):
    DataHeader: DataHeader
    Data: Data

class Messages(BaseModel):
    requestService: str
    responseService: str
    idService: str

class StatusResponse(BaseModel):
    httpError: Optional[int] = None
    status: Optional[Union[str, int]] = None

class Operation(BaseModel):
    operationDate: str
    statusResponse: StatusResponse
    type: str

class DeviceConsumer(BaseModel):
    inactiveInterval: Optional[str] = None
    ip: Optional[str] = None
    sessionTimeout: Optional[str] = None
    userAgent: Optional[str] = None
    id: Optional[str] = None
    locale: Optional[str] = None

class AppConsumer(BaseModel):
    id: str
    sessionId: str
    terminalId: Optional[str] = None
    canalId: str

class Consumer(BaseModel):
    deviceConsumer: DeviceConsumer
    appConsumer: AppConsumer

class DataObject(BaseModel):
    documento: Documento
    messages: Messages
    operation: Operation
    consumer: Consumer

class JsonPayload(BaseModel):
    dataObject: DataObject
    msm: str

class EventEntry(BaseModel):
    """
    Modelo de validación de datos trama mbaas.
    """
    logName: str
    resource: Resource
    jsonPayload: JsonPayload
    receiveTimestamp: str
    insertId: str
    timestamp: str

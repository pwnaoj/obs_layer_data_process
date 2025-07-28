"""workflow/utils/models.py"""

from pydantic import BaseModel
from typing import Any, Dict, Union, Optional, Literal


class Labels(BaseModel):
    project_id: str

class Resource(BaseModel):
    type: str
    labels: Labels

class DocumentClient(BaseModel):
    number: str
    type: str
    
class Client(BaseModel):
    documentClient: DocumentClient
    userId: str

class Transaction(BaseModel):
    transactionData: Dict[str, Any]
    transactionName: str

class Messages(BaseModel):
    idService: Literal["Observabilidad"]
    transaction: Transaction

class StatusResponse(BaseModel):
    httpCode: Optional[str] = None
    status: Optional[Union[str, int]] = None

class Operation(BaseModel):
    operationDate: str
    statusResponse: StatusResponse
    type: str

class AppConsumer(BaseModel):
    id: str
    sessionId: str
    channelId: str
    
class Consumer(BaseModel):
    ip: str
    appConsumer: AppConsumer

class DataObject(BaseModel):
    client: Client
    messages: Messages
    moduleId: str
    operation: Operation
    consumer: Consumer

class JsonPayload(BaseModel):
    dataObject: DataObject
    msm: str

class WorkflowEntry(BaseModel):
    """
    Modelo de validación de datos artefacto workflow.
    """
    logName: str
    resource: Resource
    jsonPayload: JsonPayload
    receiveTimestamp: str
    insertId: str
    timestamp: str

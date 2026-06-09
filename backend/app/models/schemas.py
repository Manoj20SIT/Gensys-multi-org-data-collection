from dataclasses import dataclass
from typing import Optional
from pydantic import BaseModel, Field
from typing import Optional, List

@dataclass
class OrgCredentials:
    org_name: str
    # account_id: str
    # active: bool
    api_base_url: str
    region: str
    client_id: str
    client_secret: str

@dataclass
class TokenEntry:
    access_token: str
    expires_at_epoch: float

@dataclass
class OrgRunResult:
    org_name: str
    # account_id: str
    status: str
    detail: Optional[str] = None

class ConnectionModel(BaseModel):
    region: str
    api_base_url: str
    client_id: str
    client_secret: str

class OrgModel(BaseModel):
    org_name: str = Field(..., min_length=1)
    connection: ConnectionModel

class OrgUpdateModel(BaseModel):
    org_name: Optional[str] = None
    connection: Optional[ConnectionModel] = None

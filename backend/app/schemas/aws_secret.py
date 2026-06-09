from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List


class SecretCreateRequest(BaseModel):
    name: str = Field(..., description="Secret name/path")
    secret_string: str = Field(..., description="Secret value as plain string")
    description: Optional[str] = None
    tags: Optional[Dict[str, str]] = None
    region: Optional[str] = None


class SecretUpdateRequest(BaseModel):
    secret_id: str = Field(..., description="Secret name or ARN")
    secret_string: str
    region: Optional[str] = None


class SecretGetRequest(BaseModel):
    secret_id: str
    region: Optional[str] = None


class SecretDeleteRequest(BaseModel):
    secret_id: str
    force_delete_without_recovery: bool = True
    recovery_window_in_days: Optional[int] = None
    region: Optional[str] = None


class SecretListRequest(BaseModel):
    region: Optional[str] = None
    max_results: int = 20


class ApiResponse(BaseModel):
    ok: bool
    message: str
    data: Optional[Dict[str, Any]] = None

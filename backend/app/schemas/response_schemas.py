from typing import List, Optional, Literal, Union
from pydantic import BaseModel, Field

# Keep a controlled vocabulary for statuses
ActivationStatus = Literal["active", "inactive", "disabled", "enabled", "unknown"]

class TaskErrorSchema(BaseModel):
    task_key: str
    api: str
    method: str

    # HTTP/API-level info
    status: Optional[int] = None
    reason: Optional[str] = None
    message: Optional[str] = None
    context_id: Optional[str] = None
    retryable: Optional[bool] = None

    # Internal/method-not-found style error fallback
    error: Optional[str] = None


class MetricsSchema(BaseModel):
    # Volume metrics
    inbound_call_count: int = 0
    outbound_call_count: int = 0
    total_call_count: int = 0
    email_count: int = 0
    chat_count: int = 0
    sms_conversations: int = 0
    social_count: int = 0
    open_messages: int = 0
    web_messaging: int = 0
    native_voice_bot: int = 0
    native_chatbot_sessions: int = 0

    # Performance metrics
    avg_call_duration: float = 0.0
    call_abandonment_rate: float = 0.0

    # Platform usage
    gpr_used: float = 0.0
    gpe_event_count: float = 0.0
    # users_page_count: int = 0
    # groups_page_count: int = 0

    # Feature activation statuses
    agent_assist: ActivationStatus = "unknown"
    knowledge: ActivationStatus = "unknown"
    wfm_activation: ActivationStatus = "unknown"
    recording_activation: ActivationStatus = "unknown"
    qm_activation: ActivationStatus = "unknown"
    survey_activation: ActivationStatus = "unknown"
    sta_activation: ActivationStatus = "unknown"
    learning_activation: ActivationStatus = "unknown"
    gamification_activation: ActivationStatus = "unknown"
    # NEW billing fields
    isInRampPeriod: Optional[bool] = None
    licenseModel: Optional[str] = None
    userCommit: float = 0.0
    userCount: float = 0.0
    seatAdoptionBucket: Optional[float] = None
    tokenCommited: float = 0.0
    tokenActual: float = 0.0
    unitOfMeasureType:Optional[str] = None


class OrgResultSchema(BaseModel):
    org_name: str
    # success: bool
    # partial_success: bool

    # expires_in: Optional[int] = None
    metrics: Optional[MetricsSchema] = None   # None for total failure org
    # error: Optional[str] = None               # high-level org error (sanitized)
    # task_errors: List[TaskErrorSchema] = Field(default_factory=list)


class RunCollectionResponseSchema(BaseModel):
    total_orgs: int
    # mode: Literal["sequential", "parallel"] = "sequential"
    requested_fields: List[str] = Field(default_factory=list)
    results: List[OrgResultSchema] = Field(default_factory=list)
    message: Optional[str] = None
    file_name: Optional[str] = None
    download_url: Optional[str] = None

from typing import Any



class ClientBuildError(Exception):
    """Raised when API client creation/auth fails."""
    pass

class AppException(Exception):
    def __init__(self, message: Any, status_code: int = 400, code: str = "APP_ERROR", context: dict | None = None):
        safe_message = message if isinstance(message, str) else str(message)
        self.message = safe_message
        self.status_code = status_code
        self.code = code
        self.context = context or {}
        super().__init__(safe_message)


class CredentialException(AppException):
    def __init__(self, message: str = "Invalid client credentials", context: dict | None = None):
        super().__init__(
            message=message,
            status_code=401,
            code="CREDENTIAL_ERROR",
            context=context
        )


class ConfigException(AppException):
    def __init__(self, message: str = "Invalid or missing configuration", context: dict | None = None):
        super().__init__(
            message=message,
            status_code=500,
            code="CONFIG_ERROR",
            context=context
        )

from typing import Any


class TaskExecutionException(Exception):
    def __init__(
        self,
        message: Any = "Task execution failed",
        task_key: str | None = None,
        api: str | None = None,
        method: str | None = None,
        status: int | None = None,
        reason: str | None = None,
        context_id: str | None = None,
        retryable: bool = False,
        raw_error: Any = None,
        raw_body: Any = None,
        headers: dict | None = None,
    ):
        super().__init__(str(message))
        self.message = str(message)
        self.task_key = task_key
        self.api = api
        self.method = method
        self.status = status
        self.reason = reason
        self.context_id = context_id
        self.retryable = retryable
        self.raw_error = raw_error
        self.raw_body = raw_body
        self.headers = headers or {}

    def to_dict(self):
        return {
            "task_key": self.task_key,
            "api": self.api,
            "method": self.method,
            "status": self.status,
            "reason": self.reason,
            "message": self.message,
            "context_id": self.context_id,
            "retryable": self.retryable,
            "raw_error": self.raw_error,
            "raw_body": self.raw_body,
            "headers": self.headers,
        }

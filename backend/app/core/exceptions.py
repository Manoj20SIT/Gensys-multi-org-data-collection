class AppException(Exception):
    def __init__(self, message: str, status_code: int = 400, code: str = "APP_ERROR", context: dict | None = None):
        self.message = message
        self.status_code = status_code
        self.code = code
        self.context = context or {}
        super().__init__(message)


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

class TaskExecutionException(AppException):
    def __init__(
        self,
        message: str = "Task execution failed",
        task_key: str | None = None,
        api: str | None = None,
        method: str | None = None,
        status: int | None = None,
        reason: str | None = None,
        context_id: str | None = None,
        retryable: bool = False,
        context: dict | None = None
    ):
        merged_context = {
            "task_key": task_key,
            "api": api,
            "method": method,
            "status": status,
            "reason": reason,
            "context_id": context_id,
            "retryable": retryable,
            **(context or {})
        }

        super().__init__(
            message=message,
            status_code=status or 500,
            code="TASK_EXECUTION_ERROR",
            context=merged_context
        )

    def to_dict(self):
        return {
            "task_key": self.context.get("task_key"),
            "api": self.context.get("api"),
            "method": self.context.get("method"),
            "status": self.context.get("status"),
            "reason": self.context.get("reason"),
            "message": self.message,
            "context_id": self.context.get("context_id"),
            "retryable": self.context.get("retryable", False),
        }

class LLMClientError(Exception):
    def __init__(self, message: str, status_code: int | None = None, original_exception: Exception | None = None):
        super().__init__(message)
        self.status_code = status_code
        self.original_exception = original_exception

    def __str__(self):
        base = super().__str__()
        if self.status_code:
            base += f" (status {self.status_code})"
        if self.original_exception:
            base += f" | Caused by: {repr(self.original_exception)}"
        return base

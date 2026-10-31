"""
Custom domain exceptions for Brightloop Subscription Management System.
"""


class BrightloopException(Exception):
    """Base exception for all domain errors."""
    def __init__(self, message: str, code: str = "INTERNAL_ERROR"):
        super().__init__(message)
        self.message = message
        self.code = code


class NotFoundError(BrightloopException):
    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, code="NOT_FOUND")


class ConflictError(BrightloopException):
    def __init__(self, message: str = "Conflict or duplicate resource"):
        super().__init__(message, code="CONFLICT")


class InvalidStateTransitionError(BrightloopException):
    def __init__(self, message: str = "Invalid state transition"):
        super().__init__(message, code="INVALID_STATE_TRANSITION")


class ExpiredError(BrightloopException):
    def __init__(self, message: str = "Resource has expired"):
        super().__init__(message, code="EXPIRED")

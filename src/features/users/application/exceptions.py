"""Application layer exceptions for User Management."""


class ApplicationException(Exception):
    """Base exception for application layer errors."""

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class InvalidCredentialsException(ApplicationException):
    """Raised when authentication credentials (email/password) are incorrect."""

    def __init__(self, message: str = "Incorrect email or password"):
        super().__init__(message)


class InvalidTokenException(ApplicationException):
    """Raised when a token cannot be validated, is expired, or is malformed."""

    def __init__(self, message: str = "Could not validate credentials"):
        super().__init__(message)


class EntityAlreadyExistsException(ApplicationException):
    """Raised when an entity with unique constraints already exists."""

    def __init__(self, field: str, message: str):
        super().__init__(message)
        self.field = field


class OCRVerificationFailedException(ApplicationException):
    """Raised when OCR validation fails to verify identity."""

    def __init__(self, message: str = "OCR verification failed"):
        super().__init__(message)

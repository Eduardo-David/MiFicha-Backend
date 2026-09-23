"""Mock adapter for IOCRService.

Used for testing and deterministic validation without calling external providers.
"""

from __future__ import annotations

from src.features.users.application.ports import IOCRService


class MockOCRService(IOCRService):
    """Deterministic mock for OCR validation."""

    def __init__(self, should_succeed: bool = True) -> None:
        self.should_succeed = should_succeed

    def verify_identity(self, identity_card: str, first_name: str, last_name: str) -> bool:
        """Simulate document verification.

        Args:
            identity_card: Document number.
            first_name: Person's first name.
            last_name: Person's last name.

        Returns:
            True if configured to succeed, False otherwise.
        """
        return self.should_succeed

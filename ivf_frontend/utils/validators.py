# ivf_frontend/utils/validators.py
import re
from typing import Tuple, Optional

class InputValidator:
    """Lightweight validation for frontend input (boolean)."""

    @staticmethod
    def _validate(message: str) -> Tuple[bool, Optional[str]]:
        if not message or not message.strip():
            return False, "empty"
        if len(message) > 10000:
            return False, "too_long"
        # simple blacklist (very small)
        if re.search(r"(eval\(|import os|rm -rf|\<\s*script)", message, flags=re.IGNORECASE):
            return False, "unsafe"
        return True, None

    @staticmethod
    def validate_message_content(message: str) -> bool:
        ok, reason = InputValidator._validate(message)
        return ok

    @staticmethod
    def get_validation_reason(message: str) -> Optional[str]:
        ok, reason = InputValidator._validate(message)
        return reason

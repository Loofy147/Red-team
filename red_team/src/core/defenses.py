from abc import ABC, abstractmethod
from typing import Tuple, Any

from .framework import DefenseConfig

class DefenseMechanism(ABC):
    """Base class for all defense mechanisms"""

    def __init__(self, config: DefenseConfig):
        self.config = config

    @abstractmethod
    def evaluate(self, value: Any) -> Tuple[bool, str]:
        """
        Evaluate if value should be blocked.
        Returns (should_block, reason)
        """
        pass

    def execute(self, value: Any) -> Tuple[bool, str]:
        """Execute defense with tracking"""
        should_block, reason = self.evaluate(value)
        self.config.trigger(should_block)
        return should_block, reason


class InputValidationDefense(DefenseMechanism):
    """Validates basic input properties"""

    def evaluate(self, value: Any) -> Tuple[bool, str]:
        if value is None:
            return True, "Rejected: null value"
        if isinstance(value, str) and value == "":
            return True, "Rejected: empty string"
        if self.config.strength >= 4:
            if not isinstance(value, (str, int, float)):
                return True, "Rejected: invalid base type"
        return False, "Passed validation"


class TypeCheckingDefense(DefenseMechanism):
    """Validates type safety"""

    def evaluate(self, value: Any) -> Tuple[bool, str]:
        # Reject complex types
        if isinstance(value, (list, dict, tuple, set)):
            return True, f"Rejected: {type(value).__name__} type"
        if hasattr(value, '__dict__') and not isinstance(value, (str, int, float)):
            return True, "Rejected: complex object"
        return False, "Passed type check"


class BoundsEnforcementDefense(DefenseMechanism):
    """Enforces size and length limits"""

    def evaluate(self, value: Any) -> Tuple[bool, str]:
        # Dynamic threshold based on strength
        max_len = 50 - (10 - self.config.strength) * 3

        if isinstance(value, str) and len(value) > max_len:
            return True, f"Rejected: string too long ({len(value)} > {max_len})"

        if isinstance(value, (list, dict)) and len(value) > max_len / 2:
            return True, f"Rejected: collection too large"

        return False, "Passed bounds check"


class SanitizationDefense(DefenseMechanism):
    """Blocks dangerous character patterns"""

    def evaluate(self, value: Any) -> Tuple[bool, str]:
        dangerous = ["'", '"', ";", "--", "/*", "*/", "DROP", "DELETE", "UNION"]

        if self.config.strength >= 8:
            dangerous.extend(["<", ">", "{", "}", "[", "]"])

        value_str = str(value).upper()
        for pattern in dangerous:
            if pattern in value_str:
                return True, f"Rejected: dangerous pattern '{pattern}'"

        return False, "Passed sanitization"


class StateProtectionDefense(DefenseMechanism):
    """Prevents state corruption attacks"""

    def evaluate(self, value: Any) -> Tuple[bool, str]:
        if isinstance(value, (dict, list)):
            value_str = str(value)
            if "_protected" in value_str or "_private" in value_str:
                return True, "Rejected: state injection attempt"
            if "exec" in value_str or "eval" in value_str:
                return True, "Rejected: code injection attempt"

        return False, "Passed state protection"


class RateLimitingDefense(DefenseMechanism):
    """Rate limiting mechanism"""

    def __init__(self, config: DefenseConfig):
        super().__init__(config)
        self.request_count = 0

    def evaluate(self, value: Any) -> Tuple[bool, str]:
        self.request_count += 1

        if self.config.strength >= 5 and self.request_count > self.config.strength * 2:
            self.request_count = 0
            return True, "Rejected: rate limit exceeded"

        return False, "Passed rate limit"


class CryptographyDefense(DefenseMechanism):
    """Cryptographic validation"""

    def evaluate(self, value: Any) -> Tuple[bool, str]:
        if self.config.strength >= 7:
            # Simulate cryptographic check
            if isinstance(value, str):
                # Check for payload tampering patterns
                if len(value) % 2 != 0 and value.count("'") > 0:
                    return True, "Rejected: crypto validation failed"

        return False, "Passed crypto check"

from typing import Any, Dict, Optional

class SimWorldError(Exception):
    """Base class for all SimWorld platform exceptions."""
    def __init__(self, message: str, detail: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.detail = detail or {}

class WorldNotFoundError(SimWorldError):
    """Raised when a specified world cannot be found."""
    def __init__(self, message: str = "World not found", detail: Optional[Dict[str, Any]] = None):
        super().__init__(message, detail)

class SimulationLimitExceededError(SimWorldError):
    """Raised when an operation exceeds account or system limits (e.g. LLM calls, agent count)."""
    def __init__(self, message: str = "Simulation limit exceeded", detail: Optional[Dict[str, Any]] = None):
        super().__init__(message, detail)

class LLMCallFailedError(SimWorldError):
    """Raised when a call to the LLM provider fails."""
    def __init__(self, message: str = "LLM call failed", detail: Optional[Dict[str, Any]] = None):
        super().__init__(message, detail)

class OrganisationNotFoundError(SimWorldError):
    """Raised when an organisation is not found."""
    def __init__(self, message: str = "Organisation not found", detail: Optional[Dict[str, Any]] = None):
        super().__init__(message, detail)

class AuthenticationError(SimWorldError):
    """Raised when authentication fails."""
    def __init__(self, message: str = "Authentication failed", detail: Optional[Dict[str, Any]] = None):
        super().__init__(message, detail)

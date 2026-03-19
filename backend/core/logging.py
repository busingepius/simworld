import logging
import json
from datetime import datetime, timezone
from typing import Any, Dict

class StructuredFormatter(logging.Formatter):
    """Formats log records as JSON with structured context."""
    def format(self, record: logging.LogRecord) -> str:
        log_data: Dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Include standard exception info if present
        if record.exc_info:
            log_data["exc_info"] = self.formatException(record.exc_info)

        # Merge any extra kwargs passed to the logger
        if hasattr(record, "kwargs") and isinstance(record.kwargs, dict): # type: ignore
            log_data.update(record.kwargs) # type: ignore

        return json.dumps(log_data)

class StructuredLogger(logging.Logger):
    """Custom logger that accepts **kwargs for structured context."""
    def _log(self, level, msg, args, exc_info=None, extra=None, stack_info=False, stacklevel=1, **kwargs):
        if extra is None:
            extra = {}
        extra['kwargs'] = kwargs
        super()._log(level, msg, args, exc_info, extra, stack_info, stacklevel)

# Setup root logger to use our custom class
logging.setLoggerClass(StructuredLogger)

def get_logger(name: str) -> logging.Logger:
    """
    Returns a configured structured logger.
    
    Returns a logger instance that accepts kwargs for structured logging context.
    """
    logger = logging.getLogger(name)
    
    # Only add handler if it doesn't already have one to avoid duplicates
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(StructuredFormatter())
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        # Prevent propagation to avoid duplicate logging if parent has handlers
        logger.propagate = False
        
    return logger

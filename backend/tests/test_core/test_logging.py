import json
import logging
import io
from core.logging import get_logger, StructuredLogger

def test_get_logger_returns_structured_logger():
    logger = get_logger("test_logger")
    assert isinstance(logger, logging.Logger)
    # The actual class created will be the one set by setLoggerClass
    assert isinstance(logger, StructuredLogger)

def test_structured_logging_output():
    logger = get_logger("test_structured_logger")
    
    # Capture output
    log_capture = io.StringIO()
    handler = logging.StreamHandler(log_capture)
    # Get the formatter from the logger's existing handler
    handler.setFormatter(logger.handlers[0].formatter)
    
    # Temporarily replace handlers
    old_handlers = logger.handlers.copy()
    logger.handlers = [handler]
    
    try:
        # Use a type ignore to avoid warning on kwargs, though our class supports it
        logger.info("simulation_started", run_id="123", world_id="456", agent_count=50) # type: ignore
        
        output = log_capture.getvalue()
        assert output != ""
        
        # Parse the JSON output
        log_data = json.loads(output)
        
        assert log_data["level"] == "INFO"
        assert log_data["logger"] == "test_structured_logger"
        assert log_data["message"] == "simulation_started"
        assert log_data["run_id"] == "123"
        assert log_data["world_id"] == "456"
        assert log_data["agent_count"] == 50
        assert "timestamp" in log_data
    finally:
        # Restore original handlers
        logger.handlers = old_handlers

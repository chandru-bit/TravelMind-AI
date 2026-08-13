import logging
import json
import sys
import time
from typing import Optional, Dict, Any
from contextvars import ContextVar

# Context variable to hold X-Request-ID across async calls
request_id_ctx: ContextVar[str] = ContextVar("request_id", default="sys-init")

class JSONFormatter(logging.Formatter):
    """Formats log records into structured JSON lines."""
    def format(self, record: logging.LogRecord) -> str:
        log_obj: Dict[str, Any] = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "service": getattr(record, "service_name", "travelmind-service"),
            "request_id": request_id_ctx.get(),
            "message": record.getMessage(),
            "logger": record.name,
        }
        
        # Add extra payload parameters if attached
        if hasattr(record, "extra_data") and isinstance(record.extra_data, dict):
            log_obj.update(record.extra_data)
            
        if record.exc_info:
            log_obj["exception"] = self.formatException(record.exc_info)
            
        return json.dumps(log_obj)

def get_logger(service_name: str) -> logging.Logger:
    """Configures and returns a structured JSON logger for the given microservice."""
    logger = logging.getLogger(service_name)
    logger.setLevel(logging.INFO)
    
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = JSONFormatter()
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
    return logger

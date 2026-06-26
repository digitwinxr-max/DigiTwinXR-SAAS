"""
Logging Manager

Structured logging with JSON support.
"""

import json
import logging
from typing import Dict, Optional, Any
from datetime import datetime
from enum import Enum
from .request_context import RequestContextManager


class LogLevel(str, Enum):
    """Log levels."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    AUDIT = "AUDIT"


class LoggingManager:
    """
    Structured logging with JSON support.
    
    Log Levels:
    - INFO
    - WARNING
    - ERROR
    - DEBUG
    - AUDIT
    
    Features:
    - JSON format support
    - Request context injection
    - Structured metadata
    """
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self) -> None:
        """Initialize logging manager."""
        self._logger = logging.getLogger("gcdtp")
        self._logger.setLevel(logging.INFO)
        
        # Console handler
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter("%(message)s"))
        self._logger.addHandler(handler)
    
    def _build_log_entry(
        self,
        level: LogLevel,
        message: str,
        metadata: Optional[Dict] = None
    ) -> Dict:
        """Build a structured log entry."""
        context = RequestContextManager.get_context()
        
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": level.value,
            "message": message,
        }
        
        # Add request context if available
        if context:
            entry["request_id"] = context.request_id
            entry["trace_id"] = context.trace_id
            if context.user_id:
                entry["user_id"] = context.user_id
            if context.organization_id:
                entry["organization_id"] = context.organization_id
        
        # Add metadata
        if metadata:
            entry["metadata"] = metadata
        
        return entry
    
    def _log(self, level: LogLevel, message: str, metadata: Optional[Dict] = None) -> None:
        """Log a message."""
        entry = self._build_log_entry(level, message, metadata)
        
        # Output as JSON
        self._logger.log(getattr(logging, level.value), json.dumps(entry))
    
    def debug(self, message: str, metadata: Optional[Dict] = None) -> None:
        """Log a debug message."""
        self._log(LogLevel.DEBUG, message, metadata)
    
    def info(self, message: str, metadata: Optional[Dict] = None) -> None:
        """Log an info message."""
        self._log(LogLevel.INFO, message, metadata)
    
    def warning(self, message: str, metadata: Optional[Dict] = None) -> None:
        """Log a warning message."""
        self._log(LogLevel.WARNING, message, metadata)
    
    def error(self, message: str, metadata: Optional[Dict] = None) -> None:
        """Log an error message."""
        self._log(LogLevel.ERROR, message, metadata)
    
    def audit(self, message: str, metadata: Optional[Dict] = None) -> None:
        """Log an audit message."""
        self._log(LogLevel.AUDIT, message, metadata)
    
    def log_request(
        self,
        method: str,
        path: str,
        status_code: int,
        duration_ms: int
    ) -> None:
        """Log an HTTP request."""
        self.info(
            f"{method} {path}",
            metadata={
                "method": method,
                "path": path,
                "status_code": status_code,
                "duration_ms": duration_ms,
                "type": "http_request"
            }
        )
    
    def log_event(
        self,
        event_type: str,
        source: str
    ) -> None:
        """Log an event."""
        self.info(
            f"Event: {event_type}",
            metadata={
                "event_type": event_type,
                "source": source,
                "type": "event"
            }
        )
    
    def set_level(self, level: LogLevel) -> None:
        """Set the log level."""
        self._logger.setLevel(getattr(logging, level.value))
    
    def add_handler(self, handler: logging.Handler) -> None:
        """Add a logging handler."""
        self._logger.addHandler(handler)
    
    def remove_handler(self, handler: logging.Handler) -> None:
        """Remove a logging handler."""
        self._logger.removeHandler(handler)

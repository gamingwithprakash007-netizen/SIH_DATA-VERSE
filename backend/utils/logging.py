"""
Structured Logging Module for DATA VERSE.
Ensures uniform logging schema: timestamp, event, verification_id, session_id, operation, result, error.
Private keys and sensitive key material are strictly excluded.
"""
import json
import logging
import sys
from datetime import datetime, timezone
from typing import Any, Dict, Optional

class StructuredLogger:
    def __init__(self, name: str = "data_verse"):
        self.logger = logging.getLogger(name)
        if not self.logger.handlers:
            handler = logging.StreamHandler(sys.stdout)
            formatter = logging.Formatter('%(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)

    def log(
        self,
        event: str,
        operation: str,
        verification_id: Optional[str] = None,
        session_id: Optional[str] = None,
        result: Optional[str] = None,
        error: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        level: int = logging.INFO
    ) -> Dict[str, Any]:
        record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event": event,
            "operation": operation,
            "verification_id": verification_id,
            "session_id": session_id,
            "result": result,
            "error": error,
            "details": details or {}
        }
        # Redact any inadvertent key exposure
        for k in list(record["details"].keys()):
            if "private" in k.lower() or "secret" in k.lower():
                record["details"][k] = "[REDACTED_SECURITY_SENSITIVE]"
                
        self.logger.log(level, json.dumps(record))
        return record

    def info(self, event: str, operation: str, **kwargs):
        return self.log(event, operation, level=logging.INFO, **kwargs)

    def warning(self, event: str, operation: str, **kwargs):
        return self.log(event, operation, level=logging.WARNING, **kwargs)

    def error(self, event: str, operation: str, **kwargs):
        return self.log(event, operation, level=logging.ERROR, **kwargs)

app_logger = StructuredLogger()

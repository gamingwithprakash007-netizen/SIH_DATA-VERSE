"""
DATA VERSE: Replay Protection & Session Nonce Ledger
Module: backend.verification.replay

Tracks verification sessions, cryptographically secure nonces, and timestamps
to detect and prevent replay attacks, duplicated packages, and expired sessions.
"""
from typing import Dict, Any, Tuple, Set
import time
from datetime import datetime, timezone
import uuid

class ReplayProtectionLedger:
    def __init__(self, session_window_seconds: int = 3600):
        self.session_window_seconds = session_window_seconds
        # In-memory fast cache; backed by database in full stack
        self.used_nonces: Set[str] = set()
        self.verified_sessions: Dict[str, Dict[str, Any]] = {}
        self.verified_signatures: Set[str] = set()

    def register_nonce(self, nonce: str) -> bool:
        """Returns True if nonce was novel and successfully registered, False if reused."""
        if not nonce:
            return False
        if nonce in self.used_nonces:
            return False
        self.used_nonces.add(nonce)
        return True

    def validate_session(
        self,
        session_id: str,
        nonce: str,
        timestamp_iso: str,
        document_id: str,
        signature_b64: str
    ) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Validates the incoming signing/verification package for replay or tampering.
        Returns: (is_valid, reason, details)
        """
        now = datetime.now(timezone.utc)
        
        # Check 1: Nonce reuse
        if nonce in self.used_nonces:
            return False, "REPLAY_NONCE_REUSED", {
                "error": "The cryptographic nonce in this verification request has already been used.",
                "nonce": nonce
            }

        # Check 2: Timestamp validity & expiration
        try:
            ts = datetime.fromisoformat(timestamp_iso.replace("Z", "+00:00"))
            age_sec = (now - ts).total_seconds()
            if age_sec < -60:  # In future by more than 1 min
                return False, "INVALID_FUTURE_TIMESTAMP", {
                    "error": "Session timestamp is in the future.",
                    "timestamp": timestamp_iso
                }
            if age_sec > self.session_window_seconds:
                return False, "SESSION_EXPIRED", {
                    "error": f"Session timestamp exceeds the maximum validity window of {self.session_window_seconds}s.",
                    "age_seconds": round(age_sec, 1)
                }
        except Exception as e:
            return False, "INVALID_TIMESTAMP_FORMAT", {"error": str(e)}

        # Check 3: Reused session ID
        if session_id in self.verified_sessions:
            prev = self.verified_sessions[session_id]
            if prev.get("document_id") != document_id or prev.get("signature") == signature_b64:
                return False, "REPLAY_SESSION_REUSED", {
                    "error": "Session identifier was already recorded in an earlier verification run.",
                    "session_id": session_id
                }

        # Record novel elements
        self.used_nonces.add(nonce)
        self.verified_sessions[session_id] = {
            "session_id": session_id,
            "document_id": document_id,
            "signature": signature_b64,
            "recorded_at": now.isoformat()
        }
        self.verified_signatures.add(signature_b64)

        return True, "SESSION_VALID", {
            "session_id": session_id,
            "nonce": nonce,
            "status": "VALID_AND_REGISTERED"
        }

replay_ledger = ReplayProtectionLedger()

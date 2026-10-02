import tempfile
"""
DATA VERSE System Configuration Module
Configures Virtual Quantum Computer, Threat Engine, Cryptography, and Server defaults.
"""
from dataclasses import dataclass, field
from typing import Dict
import os

@dataclass
class ThreatWeights:
    """Weights for the composite explainable threat score calculation."""
    hash_anomaly: float = 0.40
    signature_anomaly: float = 0.40
    measurement_anomaly: float = 0.20
    session_anomaly: float = 0.15
    replay_anomaly: float = 0.35

    def to_dict(self) -> Dict[str, float]:
        return {
            "hash_anomaly": self.hash_anomaly,
            "signature_anomaly": self.signature_anomaly,
            "measurement_anomaly": self.measurement_anomaly,
            "session_anomaly": self.session_anomaly,
            "replay_anomaly": self.replay_anomaly,
        }

@dataclass
class SystemConfig:
    # Project Identity
    PROJECT_NAME: str = "DATA VERSE"
    VERSION: str = "1.0.0-research-prototype"
    SIH_PROBLEM: str = "SIH26141"
    
    # Execution & Simulation
    DEFAULT_SHOTS: int = 1024
    MIN_SHOTS: int = 100
    MAX_SHOTS: int = 10000
    MAX_QUBITS: int = 12  # Safety cap for classical exponential state-vector simulation
    DEFAULT_NOISE_RATE: float = 0.0
    
    # Threat Classification Thresholds
    # SAFE: score < THREAT_THRESHOLD_SAFE
    # SUSPICIOUS: THREAT_THRESHOLD_SAFE <= score < THREAT_THRESHOLD_ATTACK
    # ATTACK: score >= THREAT_THRESHOLD_ATTACK
    THREAT_THRESHOLD_SAFE: float = 15.0
    THREAT_THRESHOLD_ATTACK: float = 35.0
    THREAT_WEIGHTS: ThreatWeights = field(default_factory=ThreatWeights)
    
    # Storage & Database
    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    DATABASE_PATH: str = os.environ.get("DATA_VERSE_DB", os.path.join(BASE_DIR, "data", "data_verse.db"))
    UPLOAD_DIR: str = os.path.join(BASE_DIR, "data", "uploads")
    EXPORT_DIR: str = os.path.join(BASE_DIR, "data", "exports")
    UPLOAD_LIMIT_BYTES: int = 10 * 1024 * 1024  # 10 MB limit
    
    # Server & Debug
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG_MODE: bool = True
    SESSION_EXPIRY_SECONDS: int = 3600  # 1 hour replay window

# Singleton configuration instance
settings = SystemConfig()

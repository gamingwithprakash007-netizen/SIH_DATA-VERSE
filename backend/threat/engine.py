"""
DATA VERSE: Explainable Threat Scoring Engine & Classification
Module: backend.threat.engine

Calculates a normalized threat score (0.0 to 100.0) from a weighted linear combination
of multi-layer security anomaly indicators:
1. Hash anomaly (Cryptographic document integrity)
2. Signature anomaly (Asymmetric identity integrity)
3. Measurement anomaly (Quantum statistical deviation / TVD)
4. Session anomaly (Timestamp / structure consistency)
5. Replay anomaly (Nonce / session reuse)
"""
from typing import Dict, Any, List
from backend.core.config import settings, ThreatWeights

class ThreatEvaluation:
    def __init__(
        self,
        threat_score: float,
        classification: str,
        threshold_config: Dict[str, float],
        weights_used: Dict[str, float],
        contributing_factors: Dict[str, Any],
        reasons: List[str]
    ):
        self.threat_score = threat_score
        self.classification = classification
        self.threshold_config = threshold_config
        self.weights_used = weights_used
        self.contributing_factors = contributing_factors
        self.reasons = reasons

    def to_dict(self) -> Dict[str, Any]:
        return {
            "threat_score": round(self.threat_score, 2),
            "classification": self.classification,
            "threshold_config": self.threshold_config,
            "weights_used": self.weights_used,
            "contributing_factors": self.contributing_factors,
            "reasons": self.reasons
        }

def calculate_threat_score(
    hash_valid: bool,
    signature_valid: bool,
    measurement_anomaly_score: float,
    session_valid: bool,
    replay_detected: bool,
    weights: ThreatWeights = settings.THREAT_WEIGHTS,
    safe_threshold: float = settings.THREAT_THRESHOLD_SAFE,
    attack_threshold: float = settings.THREAT_THRESHOLD_ATTACK
) -> ThreatEvaluation:
    """
    Computes explainable composite threat score and maps to SAFE, SUSPICIOUS, or ATTACK.
    """
    # Individual normalized scores (0.0 - 100.0)
    hash_score = 0.0 if hash_valid else 100.0
    sig_score = 0.0 if signature_valid else 100.0
    meas_score = max(0.0, min(100.0, float(measurement_anomaly_score)))
    sess_score = 0.0 if session_valid else 100.0
    replay_score = 100.0 if replay_detected else 0.0

    w = weights
    total_score = (
        w.hash_anomaly * hash_score +
        w.signature_anomaly * sig_score +
        w.measurement_anomaly * meas_score +
        w.session_anomaly * sess_score +
        w.replay_anomaly * replay_score
    )
    total_score = round(max(0.0, min(100.0, total_score)), 2)

    # Classification logic
    if total_score < safe_threshold:
        classification = "SAFE"
    elif total_score < attack_threshold:
        classification = "SUSPICIOUS"
    else:
        classification = "ATTACK"

    reasons = []
    if not hash_valid:
        reasons.append("Cryptographic document hash mismatch detected (Document Tampering).")
    if not signature_valid:
        reasons.append("Asymmetric digital signature verification failed (Signature Tampering or Forgery).")
    if replay_detected:
        reasons.append("Replay attack detected: cryptographic nonce or session identifier was previously recorded.")
    if not session_valid:
        reasons.append("Session metadata check failed or session timestamp has expired.")
    if meas_score > 30.0:
        reasons.append(f"Quantum measurement distribution shows significant statistical anomaly (Anomaly Score: {meas_score:.1f}/100).")

    if not reasons:
        reasons.append("All cryptographic, classical signature, quantum measurement, and session checks passed within nominal tolerance.")

    factors = {
        "document_integrity": "PASSED" if hash_valid else "FAILED",
        "signature_integrity": "PASSED" if signature_valid else "FAILED",
        "quantum_measurement": "ANOMALY" if meas_score > 30.0 else "NOMINAL",
        "session_integrity": "PASSED" if session_valid else "FAILED",
        "replay_detection": "TRIGGERED" if replay_detected else "CLEAR",
        "raw_scores": {
            "hash_anomaly": hash_score,
            "signature_anomaly": sig_score,
            "measurement_anomaly": meas_score,
            "session_anomaly": sess_score,
            "replay_anomaly": replay_score
        }
    }

    threshold_cfg = {
        "safe_limit": safe_threshold,
        "attack_limit": attack_threshold
    }

    return ThreatEvaluation(
        threat_score=total_score,
        classification=classification,
        threshold_config=threshold_cfg,
        weights_used=w.to_dict(),
        contributing_factors=factors,
        reasons=reasons
    )

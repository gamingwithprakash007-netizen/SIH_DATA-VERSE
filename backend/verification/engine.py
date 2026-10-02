"""
DATA VERSE: Comprehensive Verification Pipeline Engine
Module: backend.verification.engine

Orchestrates the complete 18-step verification workflow described in Section 20.
"""
from typing import Dict, Any, Optional
import uuid
from datetime import datetime, timezone

from backend.crypto.hashing import verify_document_integrity
from backend.crypto.signatures import KeyManager, verify_signature_ecdsa
from backend.verification.replay import replay_ledger
from backend.quantum.bell import analyze_bell_correlations
from backend.quantum.teleportation import run_quantum_teleportation
from backend.quantum.noise import NoiseModel
from backend.statistics.engine import analyze_measurement_statistics
from backend.threat.engine import calculate_threat_score, ThreatEvaluation

def run_verification_pipeline(
    document_bytes: bytes,
    signature_package_dict: Dict[str, Any],
    check_replay: bool = True,
    noise_model: Optional[NoiseModel] = None,
    seed: Optional[int] = None,
    attack_simulation_type: Optional[str] = None,
    uploaded_filename: Optional[str] = None
) -> Dict[str, Any]:
    """
    Executes full multi-layer verification:
    1. Classical hash verification
    2. Digital signature verification
    3. Replay protection validation
    4. Virtual Quantum Computer Bell-state & teleportation verification
    5. Statistical analysis (TVD, Chi2, p-value)
    6. Threat score calculation & classification (SAFE, SUSPICIOUS, ATTACK)
    """
    verification_id = f"ver_{uuid.uuid4().hex[:12]}"
    t_start = datetime.now(timezone.utc).isoformat()

    doc_id = signature_package_dict.get("document_id", "unknown")
    filename = uploaded_filename or signature_package_dict.get("filename", "unknown.pdf")
    expected_hash = signature_package_dict.get("document_hash", "")
    sig_b64 = signature_package_dict.get("signature", "")
    pub_pem = signature_package_dict.get("public_key_pem", "")
    session_id = signature_package_dict.get("session_id", "")
    nonce = signature_package_dict.get("nonce", "")
    timestamp = signature_package_dict.get("timestamp", t_start)
    quantum_meta = signature_package_dict.get("quantum_metadata", {})

    # Step 1: Classical & Cross-Format Content Hash Verification
    expected_canonical_hash = signature_package_dict.get("canonical_content_hash") or quantum_meta.get("canonical_content_hash")
    hash_valid, computed_hash, hash_details = verify_document_integrity(
        document_bytes,
        expected_hash,
        algorithm="SHA-256",
        expected_canonical_hash=expected_canonical_hash,
        filename=filename
    )

    # Step 2: Digital Signature Verification (Cross-Format Resilient)
    sig_valid = False
    try:
        pub_key = KeyManager.load_public_key_pem(pub_pem)
        # 1. Try canonical hash if verified via cross-format or available
        candidate_hashes = []
        if hash_details.get("computed_canonical_hash"):
            candidate_hashes.append(hash_details["computed_canonical_hash"])
        if expected_canonical_hash:
            candidate_hashes.append(expected_canonical_hash)
        candidate_hashes.extend([computed_hash, expected_hash])
        
        for ch in candidate_hashes:
            if ch and verify_signature_ecdsa(pub_key, sig_b64, ch):
                sig_valid = True
                break
    except Exception:
        sig_valid = False

    # Step 3: Replay & Session Protection
    replay_detected = False
    session_valid = True
    session_reason = "SESSION_VALID"
    if check_replay:
        session_valid, session_reason, _ = replay_ledger.validate_session(
            session_id=session_id,
            nonce=nonce,
            timestamp_iso=timestamp,
            document_id=doc_id,
            signature_b64=sig_b64
        )
        if "REPLAY" in session_reason:
            replay_detected = True

    # Step 4: Quantum Verification Layer (Virtual Quantum Computer)
    shots = int(quantum_meta.get("shots", 1024))
    bell_state = quantum_meta.get("bell_state", "phi_plus")
    
    # Run Bell correlation verification
    bell_res = analyze_bell_correlations(
        state_name=bell_state,
        shots=shots,
        seed=seed,
        noise_model=noise_model
    )
    
    # Run Teleportation check
    teleport_res = run_quantum_teleportation(seed=seed, noise_model=noise_model)

    # Step 5: Statistical Engine Analysis
    expected_probs = quantum_meta.get("expected_distribution", {"00": 0.5, "11": 0.5, "01": 0.0, "10": 0.0})
    stat_analysis = analyze_measurement_statistics(
        observed_counts=bell_res["counts"],
        expected_probs=expected_probs,
        shots=shots,
        noise_level=noise_model.depolarizing_prob if noise_model else 0.0
    )

    # Step 6: Threat Score Engine
    threat_eval = calculate_threat_score(
        hash_valid=hash_valid,
        signature_valid=sig_valid,
        measurement_anomaly_score=stat_analysis["anomaly_score"],
        session_valid=session_valid,
        replay_detected=replay_detected
    )

    result_payload = {
        "verification_id": verification_id,
        "timestamp": t_start,
        "document": {
            "document_id": doc_id,
            "filename": filename,
            "byte_size": len(document_bytes),
            "expected_hash": expected_hash,
            "computed_hash": computed_hash,
            "hash_valid": hash_valid,
            "hash_algorithm": hash_details.get("algorithm", "SHA-256"),
            "match_type": hash_details.get("match_type", "EXACT_BYTE_MATCH"),
            "cross_format_verified": hash_details.get("cross_format_verified", False)
        },
        "digital_signature": {
            "algorithm": "ECDSA-SECP256R1-SHA256",
            "signature_valid": sig_valid
        },
        "session_security": {
            "session_id": session_id,
            "nonce": nonce,
            "session_valid": session_valid,
            "replay_detected": replay_detected,
            "status_code": session_reason
        },
        "quantum_verification": {
            "simulator": "DATA VERSE Virtual Quantum Computer (NumPy Engine)",
            "qubits_simulated": 3,
            "bell_state": bell_state,
            "shots": shots,
            "observed_correlation": bell_res["observed_correlation"],
            "expected_correlation": bell_res["expected_correlation"],
            "correlation_deviation": bell_res["correlation_deviation"],
            "teleportation_fidelity": teleport_res["quantum_fidelity"],
            "pauli_correction": teleport_res["pauli_correction_applied"],
            "statistical_metrics": stat_analysis
        },
        "threat_evaluation": threat_eval.to_dict(),
        "attack_context": {
            "attack_simulated": attack_simulation_type or "NONE (NORMAL VERIFICATION)",
            "controlled_lab_mode": attack_simulation_type is not None
        },
        "final_classification": threat_eval.classification,
        "final_verdict": "ACCEPTED" if threat_eval.classification == "SAFE" else "REJECTED"
    }
    return result_payload

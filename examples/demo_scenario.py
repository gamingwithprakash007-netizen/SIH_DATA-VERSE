"""
DATA VERSE: Automated Demonstration Scenario (Section 56)
Executes the 4 canonical demonstration cases:
DEMO 1: Legitimate document -> SAFE (Accepted)
DEMO 2: Tampered document -> ATTACK (Rejected, Hash & Signature Mismatch)
DEMO 3: Replay attack -> ATTACK (Nonce / Session Reused)
DEMO 4: Quantum Channel Noise -> Increased TVD & Anomaly Score
"""
import sys
import os
import json

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)
import backend

from backend.qds.protocol import sign_document_qds
from backend.verification.engine import run_verification_pipeline
from backend.attacks.lab import AttackLab
from backend.quantum.noise import NoiseModel

def run_demonstration():
    print("============================================================")
    print("DATA VERSE: Automated Research Demonstration (SIH26141)")
    print("============================================================\n")

    # Sample Fictional Document
    sample_doc = (
        b"FEDERAL CYBERSECURITY AND QUANTUM READINESS GUIDELINE v4.2\n"
        b"Author: National Infrastructure Security Council\n"
        b"Classification: UNCLASSIFIED / RESEARCH REFERENCE PROTOTYPE\n"
        b"1. OBJECTIVE: Enhance post-quantum resilient identity mechanisms.\n"
        b"2. DIRECTIVE: Mandate continuous audit logging and statistical threat scoring.\n"
        b"Verification Seed: 0x9F41C2E09B74A82B\n"
    )

    print("[*] STEP 1: Signing legitimate document...")
    pkg, priv = sign_document_qds(sample_doc, filename="Government_Digital_Guideline.pdf", shots=1024, seed=42)
    pkg_dict = pkg.to_dict()
    print(f"    Document ID : {pkg.document_id}")
    print(f"    SHA-256     : {pkg.document_hash}")
    print(f"    Session ID  : {pkg.session_id}")
    print(f"    Nonce       : {pkg.nonce}")
    print(f"    Quantum Bell: {pkg.quantum_metadata['bell_state']}\n")

    # DEMO 1: Legitimate Document
    print("--- [DEMO 1]: Legitimate Document Verification ---")
    v1 = run_verification_pipeline(sample_doc, pkg_dict, check_replay=False, seed=42)
    print(f"    Threat Score   : {v1['threat_evaluation']['threat_score']}/100.0")
    print(f"    Classification : {v1['final_classification']}")
    print(f"    Verdict        : {v1['final_verdict']}")
    print(f"    Hash Status    : {'PASSED' if v1['document']['hash_valid'] else 'FAILED'}")
    print(f"    Signature      : {'VALID' if v1['digital_signature']['signature_valid'] else 'INVALID'}")
    print(f"    Teleport Fid   : {v1['quantum_verification']['teleportation_fidelity']:.4f}\n")

    # DEMO 2: Tampered Document
    print("--- [DEMO 2]: Tampered Document Attack ---")
    res2 = AttackLab.simulate_document_tampering(sample_doc, pkg_dict, tamper_offset=18, tamper_char=b'X')
    v2 = res2["verification_result"]
    print(f"    Attack Type    : {res2['attack_type']}")
    print(f"    Bytes Modified : {res2['byte_diff']['total_diff_count']} byte(s)")
    print(f"    Threat Score   : {v2['threat_evaluation']['threat_score']}/100.0")
    print(f"    Classification : {v2['final_classification']}")
    print(f"    Verdict        : {v2['final_verdict']}")
    print(f"    Reasons        : {v2['threat_evaluation']['reasons'][0]}\n")

    # DEMO 3: Replay Attack
    print("--- [DEMO 3]: Replay Attack ---")
    res3 = AttackLab.simulate_replay_attack(sample_doc, pkg_dict)
    v3 = res3["verification_result"]
    print(f"    Attack Type    : {res3['attack_type']}")
    print(f"    Reused Nonce   : {res3['nonce_reused']}")
    print(f"    Replay Detected: {v3['session_security']['replay_detected']}")
    print(f"    Threat Score   : {v3['threat_evaluation']['threat_score']}/100.0")
    print(f"    Classification : {v3['final_classification']}\n")

    # DEMO 4: Quantum Channel Noise
    print("--- [DEMO 4]: Quantum Channel Noise (35% Depolarizing) ---")
    res4 = AttackLab.simulate_quantum_noise(sample_doc, pkg_dict, depolarizing_prob=0.35, seed=42)
    v4 = res4["verification_result"]
    q_stats = v4['quantum_verification']['statistical_metrics']
    print(f"    Noise Channel  : 35% Depolarizing")
    print(f"    TVD Deviation  : {q_stats['total_variation_distance']:.4f}")
    print(f"    Chi2 Statistic : {q_stats['chi_square_stat']:.2f} (p={q_stats['p_value']:.4e})")
    print(f"    Meas Anomaly   : {q_stats['anomaly_score']:.1f}/100.0")
    print(f"    Threat Score   : {v4['threat_evaluation']['threat_score']}/100.0")
    print(f"    Classification : {v4['final_classification']}\n")

    print("============================================================")
    print("All 4 Demonstrations Completed Successfully.")
    print("============================================================")

if __name__ == "__main__":
    run_demonstration()

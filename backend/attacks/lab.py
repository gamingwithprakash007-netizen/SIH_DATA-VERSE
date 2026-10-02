"""
DATA VERSE: Controlled Attack Simulation Laboratory
Module: backend.attacks.lab

Provides controlled, reproducible cybersecurity attack scenarios to evaluate
threat detection and statistical verification capabilities:
1. Normal (Legitimate baseline)
2. Document Tampering (Byte corruption)
3. Signature Tampering (Cryptographic signature corruption)
4. Forgery Simulation (Signing under rogue unauthorized key)
5. Replay Attack (Reusing a previously verified package)
6. Quantum Channel Noise (Injecting simulated physical channel decoherence)
7. Measurement Manipulation (Altering statistical readout registers)
"""
from typing import Dict, Any, Tuple, Optional
import copy

from backend.crypto.signatures import KeyManager, sign_hash_ecdsa
from backend.crypto.hashing import inspect_byte_differences
from backend.quantum.noise import NoiseModel
from backend.verification.engine import run_verification_pipeline

class AttackLab:
    @staticmethod
    def simulate_document_tampering(
        original_bytes: bytes,
        signature_pkg: Dict[str, Any],
        tamper_offset: int = 10,
        tamper_char: bytes = b'X'
    ) -> Dict[str, Any]:
        """Alters document content bytes to simulate unauthorized document tampering."""
        tampered = bytearray(original_bytes)
        if len(tampered) > tamper_offset:
            tampered[tamper_offset] = tamper_char[0]
        else:
            tampered.extend(b"_TAMPERED_INJECTION")
        tampered_bytes = bytes(tampered)

        diff_info = inspect_byte_differences(original_bytes, tampered_bytes)
        verification_result = run_verification_pipeline(
            document_bytes=tampered_bytes,
            signature_package_dict=signature_pkg,
            check_replay=False,
            attack_simulation_type="DOCUMENT_TAMPERING"
        )
        return {
            "attack_type": "DOCUMENT_TAMPERING",
            "byte_diff": diff_info,
            "verification_result": verification_result
        }

    @staticmethod
    def simulate_signature_tampering(
        document_bytes: bytes,
        signature_pkg: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Corrupts base64 signature payload to test asymmetric integrity detection."""
        pkg_corrupt = copy.deepcopy(signature_pkg)
        raw_sig = pkg_corrupt.get("signature", "")
        # Flip characters in signature string
        corrupt_sig = (raw_sig[:-4] + "AAAA") if len(raw_sig) > 4 else "corrupted_sig"
        pkg_corrupt["signature"] = corrupt_sig

        verification_result = run_verification_pipeline(
            document_bytes=document_bytes,
            signature_package_dict=pkg_corrupt,
            check_replay=False,
            attack_simulation_type="SIGNATURE_TAMPERING"
        )
        return {
            "attack_type": "SIGNATURE_TAMPERING",
            "original_sig_preview": raw_sig[:16] + "...",
            "tampered_sig_preview": corrupt_sig[:16] + "...",
            "verification_result": verification_result
        }

    @staticmethod
    def simulate_forgery(
        document_bytes: bytes,
        signature_pkg: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Signs the document with an unauthorized rogue keypair to simulate forgery."""
        rogue_priv, rogue_pub = KeyManager.generate_ecdsa_keypair()
        doc_hash = signature_pkg["document_hash"]
        forged_sig = sign_hash_ecdsa(rogue_priv, doc_hash)

        pkg_forged = copy.deepcopy(signature_pkg)
        pkg_forged["signature"] = forged_sig  # Signed with rogue key, but claims original public key

        verification_result = run_verification_pipeline(
            document_bytes=document_bytes,
            signature_package_dict=pkg_forged,
            check_replay=False,
            attack_simulation_type="FORGERY_SIMULATION"
        )
        return {
            "attack_type": "FORGERY_SIMULATION",
            "forged_key_used": "Rogue Ephemeral ECDSA Key",
            "verification_result": verification_result
        }

    @staticmethod
    def simulate_replay_attack(
        document_bytes: bytes,
        signature_pkg: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Simulates re-transmitting an already validated package into the verification ledger."""
        # First verification to register
        run_verification_pipeline(
            document_bytes=document_bytes,
            signature_package_dict=signature_pkg,
            check_replay=True
        )
        # Second verification triggers replay detection
        second_result = run_verification_pipeline(
            document_bytes=document_bytes,
            signature_package_dict=signature_pkg,
            check_replay=True,
            attack_simulation_type="REPLAY_ATTACK"
        )
        return {
            "attack_type": "REPLAY_ATTACK",
            "nonce_reused": signature_pkg.get("nonce"),
            "session_reused": signature_pkg.get("session_id"),
            "verification_result": second_result
        }

    @staticmethod
    def simulate_quantum_noise(
        document_bytes: bytes,
        signature_pkg: Dict[str, Any],
        depolarizing_prob: float = 0.25,
        seed: Optional[int] = 42
    ) -> Dict[str, Any]:
        """Injects simulated depolarizing quantum channel noise."""
        noise = NoiseModel.depolarizing(prob=depolarizing_prob)
        verification_result = run_verification_pipeline(
            document_bytes=document_bytes,
            signature_package_dict=signature_pkg,
            check_replay=False,
            noise_model=noise,
            seed=seed,
            attack_simulation_type="QUANTUM_CHANNEL_NOISE"
        )
        return {
            "attack_type": "QUANTUM_CHANNEL_NOISE",
            "noise_injected": noise.to_dict(),
            "verification_result": verification_result
        }

    @staticmethod
    def simulate_measurement_manipulation(
        document_bytes: bytes,
        signature_pkg: Dict[str, Any],
        seed: Optional[int] = 42
    ) -> Dict[str, Any]:
        """Simulates altered readout registers to evaluate the statistical anomaly detector."""
        pkg_copy = copy.deepcopy(signature_pkg)
        # Introduce a high readout error rate
        noise = NoiseModel.readout_error(prob=0.45)
        verification_result = run_verification_pipeline(
            document_bytes=document_bytes,
            signature_package_dict=pkg_copy,
            check_replay=False,
            noise_model=noise,
            seed=seed,
            attack_simulation_type="MEASUREMENT_MANIPULATION"
        )
        return {
            "attack_type": "MEASUREMENT_MANIPULATION",
            "manipulation_rate": 0.45,
            "verification_result": verification_result
        }

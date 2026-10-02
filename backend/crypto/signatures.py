"""
DATA VERSE: Classical Digital Signature Baseline
Module: backend.crypto.signatures

Provides standard ECDSA (NIST P-256) and RSA-PSS asymmetric signature generation
and verification using standard cryptography library primitives.
"""
from typing import Dict, Any, Tuple
import base64
from cryptography.hazmat.primitives.asymmetric import ec, rsa, padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.exceptions import InvalidSignature

class KeyManager:
    """Generates and manages ephemeral or persistent keypairs for signing research."""
    @staticmethod
    def generate_ecdsa_keypair() -> Tuple[ec.EllipticCurvePrivateKey, ec.EllipticCurvePublicKey]:
        private_key = ec.generate_private_key(ec.SECP256R1())
        return private_key, private_key.public_key()

    @staticmethod
    def generate_rsa_keypair() -> Tuple[rsa.RSAPrivateKey, rsa.RSAPublicKey]:
        private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        return private_key, private_key.public_key()

    @staticmethod
    def export_public_key_pem(public_key) -> str:
        pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        return pem.decode("utf-8")

    @staticmethod
    def load_public_key_pem(pem_str: str):
        return serialization.load_pem_public_key(pem_str.encode("utf-8"))

def sign_hash_ecdsa(private_key: ec.EllipticCurvePrivateKey, document_hash_hex: str) -> str:
    """Signs a document hash string using ECDSA with SHA-256."""
    data_to_sign = document_hash_hex.encode("utf-8")
    sig_bytes = private_key.sign(data_to_sign, ec.ECDSA(hashes.SHA256()))
    return base64.b64encode(sig_bytes).decode("utf-8")

def verify_signature_ecdsa(public_key: ec.EllipticCurvePublicKey, signature_b64: str, document_hash_hex: str) -> bool:
    """Verifies an ECDSA signature against the provided document hash."""
    try:
        sig_bytes = base64.b64decode(signature_b64)
        data_to_verify = document_hash_hex.encode("utf-8")
        public_key.verify(sig_bytes, data_to_verify, ec.ECDSA(hashes.SHA256()))
        return True
    except (InvalidSignature, ValueError, Exception):
        return False

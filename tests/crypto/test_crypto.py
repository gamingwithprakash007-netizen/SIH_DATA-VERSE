import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
import backend
from backend.crypto.hashing import compute_document_hashes, verify_document_integrity, inspect_byte_differences
from backend.crypto.signatures import KeyManager, sign_hash_ecdsa, verify_signature_ecdsa

class TestCrypto(unittest.TestCase):
    def test_hashing_consistency(self):
        doc = b"DATA VERSE CRYPTO TEST"
        h = compute_document_hashes(doc)
        valid, cur, _ = verify_document_integrity(doc, h["sha256"], "SHA-256")
        self.assertTrue(valid)
        self.assertEqual(cur, h["sha256"])

    def test_tamper_detection(self):
        doc = b"AUTHENTIC DOCUMENT CONTENT"
        tampered = b"AUTHENTIC DOCUMENT XONTENT"
        h = compute_document_hashes(doc)
        valid, _, _ = verify_document_integrity(tampered, h["sha256"], "SHA-256")
        self.assertFalse(valid)
        diff = inspect_byte_differences(doc, tampered)
        self.assertGreater(diff["total_diff_count"], 0)

    def test_ecdsa_signing_and_verification(self):
        priv, pub = KeyManager.generate_ecdsa_keypair()
        doc_hash = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
        sig = sign_hash_ecdsa(priv, doc_hash)
        self.assertTrue(verify_signature_ecdsa(pub, sig, doc_hash))
        # Wrong hash fails
        self.assertFalse(verify_signature_ecdsa(pub, sig, "ffff" + doc_hash[4:]))

if __name__ == '__main__':
    unittest.main()

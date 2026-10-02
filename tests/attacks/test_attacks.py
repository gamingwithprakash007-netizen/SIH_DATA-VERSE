import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
import backend
from backend.qds.protocol import sign_document_qds
from backend.attacks.lab import AttackLab

class TestAttacks(unittest.TestCase):
    def setUp(self):
        self.doc = b"CONFIDENTIAL GOVERNMENT GUIDELINE CONTENT"
        self.pkg, self.priv = sign_document_qds(self.doc, filename="guide.pdf")

    def test_document_tampering_attack(self):
        res = AttackLab.simulate_document_tampering(self.doc, self.pkg.to_dict())
        self.assertEqual(res["attack_type"], "DOCUMENT_TAMPERING")
        v = res["verification_result"]
        self.assertEqual(v["final_classification"], "ATTACK")
        self.assertFalse(v["document"]["hash_valid"])

    def test_signature_tampering_attack(self):
        res = AttackLab.simulate_signature_tampering(self.doc, self.pkg.to_dict())
        v = res["verification_result"]
        self.assertEqual(v["final_classification"], "ATTACK")
        self.assertFalse(v["digital_signature"]["signature_valid"])

    def test_forgery_attack(self):
        res = AttackLab.simulate_forgery(self.doc, self.pkg.to_dict())
        v = res["verification_result"]
        self.assertEqual(v["final_classification"], "ATTACK")
        self.assertFalse(v["digital_signature"]["signature_valid"])

    def test_replay_attack(self):
        res = AttackLab.simulate_replay_attack(self.doc, self.pkg.to_dict())
        v = res["verification_result"]
        self.assertTrue(v["session_security"]["replay_detected"])

if __name__ == '__main__':
    unittest.main()

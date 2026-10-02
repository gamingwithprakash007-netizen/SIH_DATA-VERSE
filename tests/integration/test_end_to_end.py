import unittest
from fastapi.testclient import TestClient
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
import backend
from backend.api.app import app

class TestAPIIntegration(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_system_status(self):
        res = self.client.get("/system/status")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "OPERATIONAL")
        self.assertEqual(data["project"], "DATA VERSE")

    def test_quantum_info(self):
        res = self.client.get("/quantum/info")
        self.assertEqual(res.status_code, 200)
        self.assertIn("H", res.json()["supported_single_qubit_gates"])

    def test_bell_state_endpoint(self):
        res = self.client.post("/quantum/bell-state", json={"state_name": "phi_plus", "shots": 500})
        self.assertEqual(res.status_code, 200)
        self.assertIn("00", res.json()["counts"])

    def test_upload_sign_verify_workflow(self):
        # 1. Upload
        files = {"file": ("demo.txt", b"Sample content for DATA VERSE SIH26141")}
        up_res = self.client.post("/documents/upload", files=files)
        self.assertEqual(up_res.status_code, 200)
        doc_id = up_res.json()["document_id"]

        # 2. Sign
        sign_res = self.client.post("/sign", json={"document_id": doc_id, "shots": 500})
        self.assertEqual(sign_res.status_code, 200)
        pkg = sign_res.json()

        # 3. Verify
        ver_res = self.client.post("/verify", json={"document_id": doc_id, "signature_package": pkg, "check_replay": False})
        self.assertEqual(ver_res.status_code, 200)
        v = ver_res.json()
        self.assertEqual(v["final_classification"], "SAFE")
        self.assertEqual(v["final_verdict"], "ACCEPTED")

if __name__ == '__main__':
    unittest.main()

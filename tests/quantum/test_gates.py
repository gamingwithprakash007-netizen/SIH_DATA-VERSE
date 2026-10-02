import unittest
import math
import numpy as np
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
import backend
from backend.quantum.gates import (
    GateOperation, build_full_unitary, PAULI_X, PAULI_Y, PAULI_Z, HADAMARD, CNOT_MATRIX
)

class TestGates(unittest.TestCase):
    def test_pauli_matrices_unitarity(self):
        for name, mat in [("X", PAULI_X), ("Y", PAULI_Y), ("Z", PAULI_Z), ("H", HADAMARD)]:
            prod = mat.conj().T @ mat
            np.testing.assert_allclose(prod, np.eye(2), atol=1e-7, err_msg=f"{name} is not unitary")

    def test_pauli_x_flips(self):
        # X|0> = |1>
        res = PAULI_X @ np.array([1.0, 0.0])
        np.testing.assert_allclose(res, [0.0, 1.0])

    def test_cnot_truth_table(self):
        # 00 -> 00, 01 -> 01, 10 -> 11, 11 -> 10
        b00 = np.array([1, 0, 0, 0], dtype=complex)
        b01 = np.array([0, 1, 0, 0], dtype=complex)
        b10 = np.array([0, 0, 1, 0], dtype=complex)
        b11 = np.array([0, 0, 0, 1], dtype=complex)

        np.testing.assert_allclose(CNOT_MATRIX @ b00, b00)
        np.testing.assert_allclose(CNOT_MATRIX @ b01, b01)
        np.testing.assert_allclose(CNOT_MATRIX @ b10, b11)
        np.testing.assert_allclose(CNOT_MATRIX @ b11, b10)

    def test_build_full_unitary_embedding(self):
        # CNOT on 3-qubit system control=0, target=2
        op = GateOperation("CNOT", [0, 2])
        u = build_full_unitary(3, op)
        self.assertEqual(u.shape, (8, 8))
        # Check unitarity
        np.testing.assert_allclose(u.conj().T @ u, np.eye(8), atol=1e-7)

if __name__ == '__main__':
    unittest.main()

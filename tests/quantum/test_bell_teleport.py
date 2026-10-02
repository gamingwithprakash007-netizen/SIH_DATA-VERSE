import unittest
import numpy as np
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
import backend
from backend.quantum.qubit import Qubit
from backend.quantum.bell import create_bell_circuit, analyze_bell_correlations
from backend.quantum.teleportation import run_quantum_teleportation

class TestBellAndTeleportation(unittest.TestCase):
    def test_all_four_bell_states(self):
        for s in ["phi_plus", "phi_minus", "psi_plus", "psi_minus"]:
            res = analyze_bell_correlations(s, shots=1000, seed=42)
            self.assertTrue(res["is_entangled"])
            self.assertLess(res["correlation_deviation"], 0.2)

    def test_teleportation_fidelity_plus_state(self):
        res = run_quantum_teleportation(input_qubit=Qubit.plus(), seed=100)
        self.assertTrue(res["teleportation_successful"])
        self.assertGreaterEqual(res["quantum_fidelity"], 0.99)

    def test_teleportation_fidelity_one_state(self):
        res = run_quantum_teleportation(input_qubit=Qubit.one(), seed=101)
        self.assertTrue(res["teleportation_successful"])
        self.assertGreaterEqual(res["quantum_fidelity"], 0.99)

if __name__ == '__main__':
    unittest.main()

"""
Unit tests for single Qubit representation and properties.
"""
import unittest
import math
import numpy as np
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from backend.quantum.qubit import Qubit

class TestQubit(unittest.TestCase):
    def test_computational_basis_zero(self):
        q = Qubit.zero()
        self.assertAlmostEqual(q.alpha.real, 1.0)
        self.assertAlmostEqual(q.alpha.imag, 0.0)
        self.assertAlmostEqual(q.beta.real, 0.0)
        self.assertAlmostEqual(q.beta.imag, 0.0)
        self.assertAlmostEqual(q.probabilities[0], 1.0)
        self.assertAlmostEqual(q.probabilities[1], 0.0)

    def test_computational_basis_one(self):
        q = Qubit.one()
        self.assertAlmostEqual(q.probabilities[0], 0.0)
        self.assertAlmostEqual(q.probabilities[1], 1.0)

    def test_superposition_plus(self):
        q = Qubit.plus()
        self.assertAlmostEqual(q.probabilities[0], 0.5)
        self.assertAlmostEqual(q.probabilities[1], 0.5)
        self.assertAlmostEqual(q.alpha.real, 1.0 / math.sqrt(2.0))

    def test_normalization_auto(self):
        # Unnormalized amplitudes 3 and 4 -> norm 5 -> 0.6 and 0.8
        q = Qubit(3.0, 4.0, auto_normalize=True)
        self.assertAlmostEqual(q.probabilities[0], 0.36)
        self.assertAlmostEqual(q.probabilities[1], 0.64)
        self.assertAlmostEqual(q.alpha.real, 0.6)
        self.assertAlmostEqual(q.beta.real, 0.8)

    def test_zero_vector_fails(self):
        with self.assertRaises(ValueError):
            Qubit(0.0, 0.0)

    def test_fidelity_identical(self):
        q1 = Qubit.plus()
        q2 = Qubit.plus()
        self.assertAlmostEqual(q1.fidelity(q2), 1.0)

    def test_fidelity_orthogonal(self):
        q0 = Qubit.zero()
        q1 = Qubit.one()
        self.assertAlmostEqual(q0.fidelity(q1), 0.0)

    def test_bloch_coordinates(self):
        # |0> has Bloch coords (0, 0, 1)
        q0 = Qubit.zero()
        x, y, z = q0.bloch_coordinates()
        self.assertAlmostEqual(x, 0.0)
        self.assertAlmostEqual(y, 0.0)
        self.assertAlmostEqual(z, 1.0)

        # |1> has Bloch coords (0, 0, -1)
        q1 = Qubit.one()
        x, y, z = q1.bloch_coordinates()
        self.assertAlmostEqual(x, 0.0)
        self.assertAlmostEqual(y, 0.0)
        self.assertAlmostEqual(z, -1.0)

        # |+> has Bloch coords (1, 0, 0)
        qp = Qubit.plus()
        x, y, z = qp.bloch_coordinates()
        self.assertAlmostEqual(x, 1.0)
        self.assertAlmostEqual(y, 0.0)
        self.assertAlmostEqual(z, 0.0)

    def test_measurement_collapse(self):
        q = Qubit.zero()
        outcome = q.measure(seed=42)
        self.assertEqual(outcome, 0)
        self.assertAlmostEqual(q.probabilities[0], 1.0)

if __name__ == '__main__':
    unittest.main()

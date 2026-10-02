import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import backend

loader = unittest.TestLoader()
suite = unittest.TestSuite()

test_files = [
    "tests.quantum.test_qubit",
    "tests.quantum.test_state_vector",
    "tests.quantum.test_gates",
    "tests.quantum.test_bell_teleport",
    "tests.crypto.test_crypto",
    "tests.attacks.test_attacks",
    "tests.integration.test_end_to_end"
]

for t in test_files:
    try:
        mod = __import__(t, fromlist=['*'])
        suite.addTests(loader.loadTestsFromModule(mod))
        print(f"Loaded test module: {t}")
    except Exception as e:
        print(f"Error loading {t}: {e}")

runner = unittest.TextTestRunner(verbosity=2)
result = runner.run(suite)
sys.exit(0 if result.wasSuccessful() else 1)

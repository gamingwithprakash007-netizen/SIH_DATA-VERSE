"""
DATA VERSE: Virtual Quantum Computer - Quantum Teleportation Protocol
Module: backend.quantum.teleportation
"""
from typing import Dict, Any, Optional
import numpy as np

from backend.quantum.qubit import Qubit
from backend.quantum.state_vector import StateVector
from backend.quantum.circuit import QuantumCircuit
from backend.quantum.gates import PAULI_X, PAULI_Z
from backend.quantum.noise import NoiseModel

def run_quantum_teleportation(
    input_qubit: Optional[Qubit] = None,
    seed: Optional[int] = None,
    noise_model: Optional[NoiseModel] = None
) -> Dict[str, Any]:
    rng = np.random.default_rng(seed)
    model = noise_model or NoiseModel.ideal()

    if input_qubit is None:
        input_qubit = Qubit.plus()

    orig_alpha = input_qubit.alpha
    orig_beta = input_qubit.beta

    initial_amps = np.zeros(8, dtype=np.complex128)
    initial_amps[0] = orig_alpha
    initial_amps[4] = orig_beta
    initial_state = StateVector(3, initial_amps, auto_normalize=False)

    qc = QuantumCircuit(3)
    qc.h(1)
    qc.cx(1, 2)
    qc.cx(0, 1)
    qc.h(0)

    exec_res = qc.run(initial_state=initial_state, shots=1, seed=rng.integers(1, 1000000), noise_model=model)
    state = exec_res.final_state.amplitudes

    p_00 = abs(state[0])**2 + abs(state[1])**2
    p_01 = abs(state[2])**2 + abs(state[3])**2
    p_10 = abs(state[4])**2 + abs(state[5])**2
    p_11 = abs(state[6])**2 + abs(state[7])**2

    probs = [p_00, p_01, p_10, p_11]
    probs = [p / sum(probs) for p in probs]
    outcomes = ["00", "01", "10", "11"]
    chosen_m = rng.choice(outcomes, p=probs)
    m0, m1 = int(chosen_m[0]), int(chosen_m[1])

    if chosen_m == "00":
        bob_raw = np.array([state[0], state[1]], dtype=np.complex128)
    elif chosen_m == "01":
        bob_raw = np.array([state[2], state[3]], dtype=np.complex128)
    elif chosen_m == "10":
        bob_raw = np.array([state[4], state[5]], dtype=np.complex128)
    else:
        bob_raw = np.array([state[6], state[7]], dtype=np.complex128)

    bob_norm = np.linalg.norm(bob_raw)
    bob_state = bob_raw / bob_norm if bob_norm > 1e-15 else bob_raw

    correction_desc = "I (No correction)"
    if m1 == 1 and m0 == 1:
        bob_corrected = PAULI_Z @ (PAULI_X @ bob_state)
        correction_desc = "Z @ X (Bit and Phase flip correction)"
    elif m1 == 1 and m0 == 0:
        bob_corrected = PAULI_X @ bob_state
        correction_desc = "X (Bit flip correction)"
    elif m1 == 0 and m0 == 1:
        bob_corrected = PAULI_Z @ bob_state
        correction_desc = "Z (Phase flip correction)"
    else:
        bob_corrected = bob_state

    rec_qubit = Qubit(bob_corrected[0], bob_corrected[1])
    fidelity = input_qubit.fidelity(rec_qubit)

    return {
        "input_state": {
            "alpha": f"{orig_alpha:.4f}",
            "beta": f"{orig_beta:.4f}",
            "probabilities": [float(abs(orig_alpha)**2), float(abs(orig_beta)**2)]
        },
        "bell_measurement_bits": {
            "m0": m0,
            "m1": m1,
            "bitstring": chosen_m
        },
        "pauli_correction_applied": correction_desc,
        "reconstructed_state": {
            "alpha": f"{rec_qubit.alpha:.4f}",
            "beta": f"{rec_qubit.beta:.4f}",
            "probabilities": [float(rec_qubit.probabilities[0]), float(rec_qubit.probabilities[1])]
        },
        "quantum_fidelity": round(fidelity, 6),
        "teleportation_successful": fidelity >= 0.95,
        "circuit_depth": qc.circuit_depth,
        "gate_count": qc.gate_count,
        "execution_time_ms": exec_res.execution_time_ms,
        "noise_model": model.to_dict()
    }

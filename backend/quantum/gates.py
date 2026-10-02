"""
DATA VERSE: Virtual Quantum Computer - Quantum Gate Engine
Module: backend.quantum.gates

Implements single-qubit and multi-qubit unitary quantum gate matrices and operators.
All matrices are represented in standard computational basis using numpy.complex128.
"""
from __future__ import annotations
import math
import cmath
from typing import Dict, List, Tuple
import numpy as np

# Standard Single-Qubit Matrices
IDENTITY = np.array([[1.0, 0.0], [0.0, 1.0]], dtype=np.complex128)
PAULI_X = np.array([[0.0, 1.0], [1.0, 0.0]], dtype=np.complex128)
PAULI_Y = np.array([[0.0, -1.0j], [1.0j, 0.0]], dtype=np.complex128)
PAULI_Z = np.array([[1.0, 0.0], [0.0, -1.0]], dtype=np.complex128)
HADAMARD = (1.0 / math.sqrt(2.0)) * np.array([[1.0, 1.0], [1.0, -1.0]], dtype=np.complex128)
PHASE_S = np.array([[1.0, 0.0], [0.0, 1.0j]], dtype=np.complex128)
PHASE_T = np.array([[1.0, 0.0], [0.0, cmath.exp(1j * math.pi / 4.0)]], dtype=np.complex128)
S_DAGGER = np.array([[1.0, 0.0], [0.0, -1.0j]], dtype=np.complex128)
T_DAGGER = np.array([[1.0, 0.0], [0.0, cmath.exp(-1j * math.pi / 4.0)]], dtype=np.complex128)

def rx_gate(theta: float) -> np.ndarray:
    c = math.cos(theta / 2.0)
    s = math.sin(theta / 2.0)
    return np.array([[c, -1j * s], [-1j * s, c]], dtype=np.complex128)

def ry_gate(theta: float) -> np.ndarray:
    c = math.cos(theta / 2.0)
    s = math.sin(theta / 2.0)
    return np.array([[c, -s], [s, c]], dtype=np.complex128)

def rz_gate(theta: float) -> np.ndarray:
    return np.array([[cmath.exp(-1j * theta / 2.0), 0.0],
                     [0.0, cmath.exp(1j * theta / 2.0)]], dtype=np.complex128)

def phase_gate(phi: float) -> np.ndarray:
    return np.array([[1.0, 0.0], [0.0, cmath.exp(1j * phi)]], dtype=np.complex128)

CNOT_MATRIX = np.array([
    [1.0, 0.0, 0.0, 0.0],
    [0.0, 1.0, 0.0, 0.0],
    [0.0, 0.0, 0.0, 1.0],
    [0.0, 0.0, 1.0, 0.0]
], dtype=np.complex128)

CZ_MATRIX = np.array([
    [1.0, 0.0, 0.0, 0.0],
    [0.0, 1.0, 0.0, 0.0],
    [0.0, 0.0, 1.0, 0.0],
    [0.0, 0.0, 0.0, -1.0]
], dtype=np.complex128)

SWAP_MATRIX = np.array([
    [1.0, 0.0, 0.0, 0.0],
    [0.0, 0.0, 1.0, 0.0],
    [0.0, 1.0, 0.0, 0.0],
    [0.0, 0.0, 0.0, 1.0]
], dtype=np.complex128)

class GateOperation:
    def __init__(self, name: str, qubits: List[int], params: Tuple[float, ...] = ()):
        self.name = name.upper()
        self.qubits = list(qubits)
        self.params = tuple(params)

    def get_matrix(self) -> np.ndarray:
        if self.name == "X":
            return PAULI_X
        elif self.name == "Y":
            return PAULI_Y
        elif self.name == "Z":
            return PAULI_Z
        elif self.name == "H":
            return HADAMARD
        elif self.name == "S":
            return PHASE_S
        elif self.name == "T":
            return PHASE_T
        elif self.name == "S_DAG":
            return S_DAGGER
        elif self.name == "T_DAG":
            return T_DAGGER
        elif self.name == "I":
            return IDENTITY
        elif self.name == "RX":
            return rx_gate(self.params[0] if self.params else 0.0)
        elif self.name == "RY":
            return ry_gate(self.params[0] if self.params else 0.0)
        elif self.name == "RZ":
            return rz_gate(self.params[0] if self.params else 0.0)
        elif self.name == "PHASE":
            return phase_gate(self.params[0] if self.params else 0.0)
        elif self.name in ("CNOT", "CX"):
            return CNOT_MATRIX
        elif self.name == "CZ":
            return CZ_MATRIX
        elif self.name == "SWAP":
            return SWAP_MATRIX
        else:
            raise ValueError(f"Unknown gate name: {self.name}")

    def __repr__(self) -> str:
        param_str = f"({', '.join(f'{p:.3f}' for p in self.params)})" if self.params else ""
        return f"{self.name}{param_str}[{', '.join(str(q) for q in self.qubits)}]"

def build_full_unitary(num_qubits: int, operation: GateOperation) -> np.ndarray:
    dim = 1 << num_qubits
    name = operation.name
    qubits = operation.qubits

    for q in qubits:
        if q < 0 or q >= num_qubits:
            raise ValueError(f"Qubit index {q} out of bounds for {num_qubits}-qubit system.")

    if len(qubits) == 1:
        target = qubits[0]
        gate_mat = operation.get_matrix()
        matrices = [IDENTITY] * num_qubits
        matrices[target] = gate_mat
        res = matrices[0]
        for m in matrices[1:]:
            res = np.kron(res, m)
        return res

    elif len(qubits) == 2:
        c, t = qubits[0], qubits[1]
        if c == t:
            raise ValueError("Control and target qubits cannot be the same.")

        if name in ("CNOT", "CX"):
            proj0 = np.array([[1.0, 0.0], [0.0, 0.0]], dtype=np.complex128)
            proj1 = np.array([[0.0, 0.0], [0.0, 1.0]], dtype=np.complex128)

            m0 = [IDENTITY] * num_qubits
            m0[c] = proj0
            res0 = m0[0]
            for m in m0[1:]:
                res0 = np.kron(res0, m)

            m1 = [IDENTITY] * num_qubits
            m1[c] = proj1
            m1[t] = PAULI_X
            res1 = m1[0]
            for m in m1[1:]:
                res1 = np.kron(res1, m)

            return res0 + res1

        elif name == "CZ":
            proj0 = np.array([[1.0, 0.0], [0.0, 0.0]], dtype=np.complex128)
            proj1 = np.array([[0.0, 0.0], [0.0, 1.0]], dtype=np.complex128)

            m0 = [IDENTITY] * num_qubits
            m0[c] = proj0
            res0 = m0[0]
            for m in m0[1:]:
                res0 = np.kron(res0, m)

            m1 = [IDENTITY] * num_qubits
            m1[c] = proj1
            m1[t] = PAULI_Z
            res1 = m1[0]
            for m in m1[1:]:
                res1 = np.kron(res1, m)

            return res0 + res1

        elif name == "SWAP":
            cnot1 = build_full_unitary(num_qubits, GateOperation("CNOT", [c, t]))
            cnot2 = build_full_unitary(num_qubits, GateOperation("CNOT", [t, c]))
            return cnot1 @ cnot2 @ cnot1

        else:
            raise ValueError(f"Unsupported 2-qubit gate: {name}")

    else:
        raise ValueError(f"Gates on {len(qubits)} qubits not supported.")

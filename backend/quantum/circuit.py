"""
DATA VERSE: Virtual Quantum Computer - Circuit Engine
Module: backend.quantum.circuit
"""
from __future__ import annotations
import time
from typing import Dict, List, Optional, Tuple, Any
import numpy as np

from backend.quantum.state_vector import StateVector
from backend.quantum.gates import (
    GateOperation,
    build_full_unitary,
    PAULI_X,
    PAULI_Y,
    PAULI_Z,
    IDENTITY
)
from backend.quantum.noise import NoiseModel

class CircuitExecutionResult:
    def __init__(
        self,
        final_state: StateVector,
        counts: Dict[str, int],
        probabilities: Dict[str, float],
        execution_time_ms: float,
        circuit_depth: int,
        gate_count: int,
        num_qubits: int,
        noise_model_summary: Dict[str, Any]
    ):
        self.final_state = final_state
        self.counts = counts
        self.probabilities = probabilities
        self.execution_time_ms = execution_time_ms
        self.circuit_depth = circuit_depth
        self.gate_count = gate_count
        self.num_qubits = num_qubits
        self.noise_model_summary = noise_model_summary

    def to_dict(self) -> Dict[str, Any]:
        return {
            "num_qubits": self.num_qubits,
            "circuit_depth": self.circuit_depth,
            "gate_count": self.gate_count,
            "execution_time_ms": round(self.execution_time_ms, 3),
            "counts": self.counts,
            "probabilities": {k: round(v, 6) for k, v in self.probabilities.items()},
            "noise_model": self.noise_model_summary,
            "state_vector_preview": [
                {"state": f"|{k}>", "probability": round(v, 6)}
                for k, v in sorted(self.probabilities.items(), key=lambda x: x[1], reverse=True)[:8]
            ]
        }

class QuantumCircuit:
    def __init__(self, num_qubits: int):
        if num_qubits < 1:
            raise ValueError(f"Circuit requires at least 1 qubit, got {num_qubits}")
        self.num_qubits = num_qubits
        self.operations: List[GateOperation] = []

    def h(self, target: int) -> "QuantumCircuit":
        self.operations.append(GateOperation("H", [target]))
        return self

    def x(self, target: int) -> "QuantumCircuit":
        self.operations.append(GateOperation("X", [target]))
        return self

    def y(self, target: int) -> "QuantumCircuit":
        self.operations.append(GateOperation("Y", [target]))
        return self

    def z(self, target: int) -> "QuantumCircuit":
        self.operations.append(GateOperation("Z", [target]))
        return self

    def s(self, target: int) -> "QuantumCircuit":
        self.operations.append(GateOperation("S", [target]))
        return self

    def t(self, target: int) -> "QuantumCircuit":
        self.operations.append(GateOperation("T", [target]))
        return self

    def s_dag(self, target: int) -> "QuantumCircuit":
        self.operations.append(GateOperation("S_DAG", [target]))
        return self

    def t_dag(self, target: int) -> "QuantumCircuit":
        self.operations.append(GateOperation("T_DAG", [target]))
        return self

    def rx(self, target: int, theta: float) -> "QuantumCircuit":
        self.operations.append(GateOperation("RX", [target], params=(theta,)))
        return self

    def ry(self, target: int, theta: float) -> "QuantumCircuit":
        self.operations.append(GateOperation("RY", [target], params=(theta,)))
        return self

    def rz(self, target: int, theta: float) -> "QuantumCircuit":
        self.operations.append(GateOperation("RZ", [target], params=(theta,)))
        return self

    def phase(self, target: int, phi: float) -> "QuantumCircuit":
        self.operations.append(GateOperation("PHASE", [target], params=(phi,)))
        return self

    def cx(self, control: int, target: int) -> "QuantumCircuit":
        self.operations.append(GateOperation("CNOT", [control, target]))
        return self

    def cnot(self, control: int, target: int) -> "QuantumCircuit":
        return self.cx(control, target)

    def cz(self, control: int, target: int) -> "QuantumCircuit":
        self.operations.append(GateOperation("CZ", [control, target]))
        return self

    def swap(self, q1: int, q2: int) -> "QuantumCircuit":
        self.operations.append(GateOperation("SWAP", [q1, q2]))
        return self

    def apply_gate(self, name: str, *qubits: int, **params: float) -> "QuantumCircuit":
        param_vals = tuple(params.values())
        self.operations.append(GateOperation(name, list(qubits), params=param_vals))
        return self

    @property
    def gate_count(self) -> int:
        return len(self.operations)

    @property
    def circuit_depth(self) -> int:
        qubit_depths = [0] * self.num_qubits
        for op in self.operations:
            active_qubits = op.qubits
            current_max = max(qubit_depths[q] for q in active_qubits) if active_qubits else 0
            for q in active_qubits:
                qubit_depths[q] = current_max + 1
        return max(qubit_depths) if qubit_depths else 0

    def run(
        self,
        initial_state: Optional[StateVector] = None,
        shots: int = 1024,
        seed: Optional[int] = None,
        noise_model: Optional[NoiseModel] = None
    ) -> CircuitExecutionResult:
        t0 = time.perf_counter()
        rng = np.random.default_rng(seed)
        model = noise_model or NoiseModel.ideal()

        if initial_state is None:
            current_state = StateVector.zero_state(self.num_qubits)
        else:
            if initial_state.num_qubits != self.num_qubits:
                raise ValueError("Initial state qubit count does not match circuit.")
            current_state = initial_state.copy()

        for op in self.operations:
            gate_u = build_full_unitary(self.num_qubits, op)
            current_state.amplitudes = gate_u @ current_state.amplitudes

            if model.is_noisy():
                for q in op.qubits:
                    if model.depolarizing_prob > 0.0 and rng.random() < model.depolarizing_prob:
                        choice = rng.choice(["X", "Y", "Z"])
                        noise_u = build_full_unitary(self.num_qubits, GateOperation(choice, [q]))
                        current_state.amplitudes = noise_u @ current_state.amplitudes
                    elif model.bit_flip_prob > 0.0 and rng.random() < model.bit_flip_prob:
                        noise_u = build_full_unitary(self.num_qubits, GateOperation("X", [q]))
                        current_state.amplitudes = noise_u @ current_state.amplitudes
                    elif model.phase_flip_prob > 0.0 and rng.random() < model.phase_flip_prob:
                        noise_u = build_full_unitary(self.num_qubits, GateOperation("Z", [q]))
                        current_state.amplitudes = noise_u @ current_state.amplitudes

        current_state.normalize()
        probs_dict = current_state.get_probability_dict()

        raw_counts = current_state.sample_shots(shots=shots, seed=rng.integers(1, 1000000))

        final_counts: Dict[str, int] = {k: 0 for k in probs_dict.keys()}
        if model.measurement_error_prob > 0.0:
            for bitstr, cnt in raw_counts.items():
                for _ in range(cnt):
                    noisy_bitstr = model.apply_readout_noise(bitstr, rng)
                    final_counts[noisy_bitstr] = final_counts.get(noisy_bitstr, 0) + 1
        else:
            final_counts = raw_counts

        elapsed_ms = (time.perf_counter() - t0) * 1000.0

        return CircuitExecutionResult(
            final_state=current_state,
            counts=final_counts,
            probabilities=probs_dict,
            execution_time_ms=elapsed_ms,
            circuit_depth=self.circuit_depth,
            gate_count=self.gate_count,
            num_qubits=self.num_qubits,
            noise_model_summary=model.to_dict()
        )

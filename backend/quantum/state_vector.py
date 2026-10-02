"""
DATA VERSE: Virtual Quantum Computer - Multi-Qubit State Vector Engine
Module: backend.quantum.state_vector

Implements n-qubit pure state representation in Hilbert space of dimension 2^n.
"""
from __future__ import annotations
import math
from typing import Dict, List, Optional, Tuple, Sequence
import numpy as np
from backend.quantum.qubit import Qubit

class StateVector:
    """
    Representation of an n-qubit quantum state vector in C^(2^n).
    Basis ordering: |q_0 q_1 ... q_{n-1}> where q_0 is most-significant qubit index.
    """
    def __init__(self, num_qubits: int, amplitudes: Optional[Sequence[complex]] = None, auto_normalize: bool = True):
        if num_qubits < 1:
            raise ValueError(f"Number of qubits must be >= 1, got {num_qubits}")
            
        self.num_qubits: int = num_qubits
        self.dimension: int = 1 << num_qubits  # 2^n
        
        if amplitudes is None:
            # Default state |00...0>
            self.amplitudes = np.zeros(self.dimension, dtype=np.complex128)
            self.amplitudes[0] = 1.0 + 0.0j
        else:
            arr = np.asarray(amplitudes, dtype=np.complex128)
            if arr.shape != (self.dimension,):
                raise ValueError(
                    f"Dimension mismatch for {num_qubits} qubits: expected {self.dimension} amplitudes, got {arr.shape[0]}"
                )
            norm_sq = np.sum(np.abs(arr)**2)
            if norm_sq < 1e-15:
                raise ValueError("Zero amplitude state vector cannot be normalized.")
            if auto_normalize:
                self.amplitudes = arr / math.sqrt(norm_sq)
            else:
                if not math.isclose(norm_sq, 1.0, abs_tol=1e-7):
                    raise ValueError(f"State amplitudes are not normalized: sum(|c_i|²) = {norm_sq:.8f}")
                self.amplitudes = arr

    @classmethod
    def zero_state(cls, num_qubits: int) -> StateVector:
        """Initializes the |0...0> state for n qubits."""
        return cls(num_qubits)

    @classmethod
    def from_qubits(cls, qubits: Sequence[Qubit]) -> StateVector:
        """Constructs an n-qubit product state via tensor products of individual qubits."""
        if not qubits:
            raise ValueError("Qubit sequence must not be empty.")
            
        current = qubits[0].state_vector
        for q in qubits[1:]:
            current = np.kron(current, q.state_vector)
            
        return cls(num_qubits=len(qubits), amplitudes=current, auto_normalize=False)

    def normalize(self) -> None:
        """Normalizes amplitudes to unit Euclidean norm."""
        norm = np.linalg.norm(self.amplitudes)
        if norm < 1e-15:
            raise ValueError("Norm too close to zero; cannot normalize.")
        self.amplitudes = self.amplitudes / norm

    @property
    def probabilities(self) -> np.ndarray:
        """Returns Born rule probability distribution across all 2^n basis states."""
        return np.abs(self.amplitudes)**2

    def get_probability_dict(self) -> Dict[str, float]:
        """Returns mapping from bitstring to probability: {'00': p0, '01': p1, ...}."""
        probs = self.probabilities
        result = {}
        for i, p in enumerate(probs):
            bitstr = format(i, f'0{self.num_qubits}b')
            result[bitstr] = float(p)
        return result

    def tensor_product(self, other: StateVector) -> StateVector:
        """
        Computes the Kronecker / tensor product |ψ> ⊗ |φ>.
        Yields an (n + m)-qubit state vector of dimension 2^(n + m).
        """
        new_amplitudes = np.kron(self.amplitudes, other.amplitudes)
        return StateVector(
            num_qubits=self.num_qubits + other.num_qubits,
            amplitudes=new_amplitudes,
            auto_normalize=False
        )

    def inner_product(self, other: StateVector) -> complex:
        """Computes Dirac bracket inner product <self | other>."""
        if self.num_qubits != other.num_qubits:
            raise ValueError(
                f"Cannot compute inner product between mismatched dimensions: {self.num_qubits} vs {other.num_qubits} qubits"
            )
        return complex(np.vdot(self.amplitudes, other.amplitudes))

    def fidelity(self, other: StateVector) -> float:
        """Computes state fidelity F(|ψ>, |φ>) = |<ψ|φ>|²."""
        braket = self.inner_product(other)
        return float(abs(braket)**2)

    def sample_shots(self, shots: int = 1024, seed: Optional[int] = None) -> Dict[str, int]:
        """
        Samples projective computational-basis measurements according to Born probabilities.
        Returns histogram dictionary: {'00': count_00, '01': count_01, ...}
        """
        if shots < 1:
            raise ValueError(f"Shots must be >= 1, got {shots}")
            
        rng = np.random.default_rng(seed)
        probs = self.probabilities
        
        # Ensure probabilities strictly sum to 1.0 to avoid floating point drift
        probs = probs / np.sum(probs)
        
        outcomes = rng.choice(self.dimension, size=shots, p=probs)
        counts_arr = np.bincount(outcomes, minlength=self.dimension)
        
        result: Dict[str, int] = {}
        for i, count in enumerate(counts_arr):
            bitstr = format(i, f'0{self.num_qubits}b')
            result[bitstr] = int(count)
        return result

    def copy(self) -> StateVector:
        """Returns a deep copy of the state vector."""
        return StateVector(self.num_qubits, self.amplitudes.copy(), auto_normalize=False)

    def __repr__(self) -> str:
        top_states = []
        for bitstr, p in self.get_probability_dict().items():
            if p > 0.001:
                top_states.append(f"|{bitstr}>: {p*100:.1f}%")
        preview = ", ".join(top_states[:4])
        if len(top_states) > 4:
            preview += ", ..."
        return f"StateVector(qubits={self.num_qubits}, dim={self.dimension}, states=[{preview}])"

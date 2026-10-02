"""
DATA VERSE: Virtual Quantum Computer - Single Qubit Engine
Module: backend.quantum.qubit

Implements a single qubit representation:
|ψ> = α|0> + β|1> with |α|² + |β|² = 1.
"""
from __future__ import annotations
import cmath
import math
from typing import Tuple, Optional
import numpy as np

class Qubit:
    """
    Representation of a single quantum bit (qubit) state vector in C^2.
    """
    def __init__(self, alpha: complex = 1.0 + 0.0j, beta: complex = 0.0 + 0.0j, auto_normalize: bool = True):
        self.alpha: complex = complex(alpha)
        self.beta: complex = complex(beta)
        
        norm_sq = abs(self.alpha)**2 + abs(self.beta)**2
        if norm_sq < 1e-15:
            raise ValueError("Zero amplitude state vector cannot be normalized.")
            
        if auto_normalize:
            self.normalize()
        else:
            if not math.isclose(norm_sq, 1.0, abs_tol=1e-7):
                raise ValueError(f"State amplitudes are not normalized: |α|² + |β|² = {norm_sq:.8f}")

    @classmethod
    def zero(cls) -> Qubit:
        """Initialize in computational basis state |0>."""
        return cls(1.0 + 0.0j, 0.0 + 0.0j, auto_normalize=False)

    @classmethod
    def one(cls) -> Qubit:
        """Initialize in computational basis state |1>."""
        return cls(0.0 + 0.0j, 1.0 + 0.0j, auto_normalize=False)

    @classmethod
    def plus(cls) -> Qubit:
        """Initialize in Hadamard superposition state |+> = (|0> + |1>)/√2."""
        inv_sqrt2 = 1.0 / math.sqrt(2.0)
        return cls(inv_sqrt2, inv_sqrt2, auto_normalize=False)

    @classmethod
    def minus(cls) -> Qubit:
        """Initialize in Hadamard superposition state |-> = (|0> - |1>)/√2."""
        inv_sqrt2 = 1.0 / math.sqrt(2.0)
        return cls(inv_sqrt2, -inv_sqrt2, auto_normalize=False)

    @classmethod
    def from_angles(cls, theta: float, phi: float) -> Qubit:
        """
        Initialize state on the Bloch sphere:
        |ψ> = cos(θ/2)|0> + e^(iφ)sin(θ/2)|1>
        """
        alpha = math.cos(theta / 2.0)
        beta = cmath.exp(1j * phi) * math.sin(theta / 2.0)
        return cls(alpha, beta, auto_normalize=False)

    def normalize(self) -> None:
        """Normalizes the state vector so |α|² + |β|² = 1."""
        norm = math.sqrt(abs(self.alpha)**2 + abs(self.beta)**2)
        if norm < 1e-15:
            raise ValueError("Norm too close to zero; cannot normalize.")
        self.alpha /= norm
        self.beta /= norm

    @property
    def state_vector(self) -> np.ndarray:
        """Returns 2x1 complex state vector [α, β]^T."""
        return np.array([self.alpha, self.beta], dtype=np.complex128)

    @property
    def probabilities(self) -> np.ndarray:
        """Calculates probabilities P(0) = |α|² and P(1) = |β|²."""
        return np.array([abs(self.alpha)**2, abs(self.beta)**2], dtype=np.float64)

    def measure(self, seed: Optional[int] = None) -> int:
        """
        Simulates computational basis projective measurement.
        Collapses the state to either |0> or |1> according to Born rule probabilities.
        Returns outcome bit: 0 or 1.
        """
        rng = np.random.default_rng(seed)
        p0 = abs(self.alpha)**2
        outcome = 0 if rng.random() < p0 else 1
        
        # State collapse
        if outcome == 0:
            self.alpha = 1.0 + 0.0j
            self.beta = 0.0 + 0.0j
        else:
            self.alpha = 0.0 + 0.0j
            self.beta = 1.0 + 0.0j
            
        return outcome

    def fidelity(self, other: Qubit) -> float:
        """
        Calculates quantum state fidelity F(|ψ>, |φ>) = |<ψ|φ>|².
        """
        inner_prod = np.vdot(self.state_vector, other.state_vector)
        return float(abs(inner_prod)**2)

    def bloch_coordinates(self) -> Tuple[float, float, float]:
        """
        Computes (x, y, z) coordinates on the unit Bloch sphere.
        x = 2 * Re(α* β)
        y = 2 * Im(α* β)
        z = |α|² - |β|²
        """
        alpha_conj = self.alpha.conjugate()
        prod = alpha_conj * self.beta
        x = float(2.0 * prod.real)
        y = float(2.0 * prod.imag)
        z = float(abs(self.alpha)**2 - abs(self.beta)**2)
        return (x, y, z)

    def __repr__(self) -> str:
        return f"Qubit(α={self.alpha:.4f}, β={self.beta:.4f}, P(0)={abs(self.alpha)**2:.4f}, P(1)={abs(self.beta)**2:.4f})"

"""
DATA VERSE: Virtual Quantum Computer - Quantum Channel Noise Models
Module: backend.quantum.noise
"""
from dataclasses import dataclass
from typing import Optional, List, Dict
import numpy as np

@dataclass
class NoiseModel:
    bit_flip_prob: float = 0.0
    phase_flip_prob: float = 0.0
    depolarizing_prob: float = 0.0
    measurement_error_prob: float = 0.0
    model_name: str = "ideal"

    @classmethod
    def ideal(cls) -> "NoiseModel":
        return cls(model_name="ideal")

    @classmethod
    def depolarizing(cls, prob: float) -> "NoiseModel":
        return cls(depolarizing_prob=prob, model_name=f"depolarizing_{prob:.3f}")

    @classmethod
    def bit_flip(cls, prob: float) -> "NoiseModel":
        return cls(bit_flip_prob=prob, model_name=f"bit_flip_{prob:.3f}")

    @classmethod
    def phase_flip(cls, prob: float) -> "NoiseModel":
        return cls(phase_flip_prob=prob, model_name=f"phase_flip_{prob:.3f}")

    @classmethod
    def readout_error(cls, prob: float) -> "NoiseModel":
        return cls(measurement_error_prob=prob, model_name=f"readout_error_{prob:.3f}")

    def is_noisy(self) -> bool:
        return (
            self.bit_flip_prob > 0.0 or
            self.phase_flip_prob > 0.0 or
            self.depolarizing_prob > 0.0 or
            self.measurement_error_prob > 0.0
        )

    def apply_readout_noise(self, bitstring: str, rng: np.random.Generator) -> str:
        if self.measurement_error_prob <= 0.0:
            return bitstring
        bits = list(bitstring)
        for i in range(len(bits)):
            if rng.random() < self.measurement_error_prob:
                bits[i] = '1' if bits[i] == '0' else '0'
        return "".join(bits)

    def to_dict(self) -> Dict[str, float]:
        return {
            "model_name": self.model_name,
            "bit_flip_prob": self.bit_flip_prob,
            "phase_flip_prob": self.phase_flip_prob,
            "depolarizing_prob": self.depolarizing_prob,
            "measurement_error_prob": self.measurement_error_prob,
        }

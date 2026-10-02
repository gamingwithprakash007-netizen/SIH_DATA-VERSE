"""
DATA VERSE: Virtual Quantum Computer - Bell State & Entanglement Engine
Module: backend.quantum.bell
"""
from typing import Dict, Any, Optional
from backend.quantum.circuit import QuantumCircuit
from backend.quantum.noise import NoiseModel

BELL_STATES = ["phi_plus", "phi_minus", "psi_plus", "psi_minus"]

def create_bell_circuit(state_name: str = "phi_plus") -> QuantumCircuit:
    normalized = state_name.lower().replace("-", "_").replace(" ", "_")
    qc = QuantumCircuit(2)

    if normalized in ("phi_plus", "phi+", "b00"):
        qc.h(0)
        qc.cx(0, 1)
    elif normalized in ("phi_minus", "phi-", "b10"):
        qc.x(0)
        qc.h(0)
        qc.cx(0, 1)
    elif normalized in ("psi_plus", "psi+", "b01"):
        qc.x(1)
        qc.h(0)
        qc.cx(0, 1)
    elif normalized in ("psi_minus", "psi-", "b11"):
        qc.x(0)
        qc.x(1)
        qc.h(0)
        qc.cx(0, 1)
    else:
        raise ValueError(f"Unknown Bell state '{state_name}'. Choose from: {BELL_STATES}")

    return qc

def analyze_bell_correlations(
    state_name: str,
    shots: int = 1024,
    seed: Optional[int] = None,
    noise_model: Optional[NoiseModel] = None
) -> Dict[str, Any]:
    qc = create_bell_circuit(state_name)
    res = qc.run(shots=shots, seed=seed, noise_model=noise_model)

    counts = res.counts
    total = sum(counts.values())

    c00 = counts.get("00", 0)
    c11 = counts.get("11", 0)
    c01 = counts.get("01", 0)
    c10 = counts.get("10", 0)

    observed_corr = ((c00 + c11) - (c01 + c10)) / float(total) if total > 0 else 0.0

    normalized = state_name.lower().replace("-", "_")
    if "phi" in normalized:
        expected_corr = 1.0
        expected_distribution = {"00": 0.5, "11": 0.5, "01": 0.0, "10": 0.0}
    else:
        expected_corr = -1.0
        expected_distribution = {"01": 0.5, "10": 0.5, "00": 0.0, "11": 0.0}

    deviation = abs(observed_corr - expected_corr)

    return {
        "bell_state": state_name,
        "shots": shots,
        "circuit_depth": res.circuit_depth,
        "gate_count": res.gate_count,
        "counts": counts,
        "probabilities": res.probabilities,
        "expected_distribution": expected_distribution,
        "observed_correlation": round(observed_corr, 4),
        "expected_correlation": expected_corr,
        "correlation_deviation": round(deviation, 4),
        "is_entangled": deviation < 0.25,
        "execution_time_ms": res.execution_time_ms,
        "noise_model": res.noise_model_summary
    }

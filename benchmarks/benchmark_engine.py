"""
DATA VERSE: Virtual Quantum Computer Benchmarking Suite
Module: benchmarks.benchmark_engine

Measures execution time, memory usage, circuit depth, and shot scaling
across 2 to 10 qubits. Saves results in CSV and JSON formats.
"""
import time
import os
import csv
import json
import resource
from typing import Dict, Any, List
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np

from backend.quantum.circuit import QuantumCircuit

def get_memory_usage_mb() -> float:
    """Returns maximum resident set size in megabytes."""
    usage = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    # On Linux ru_maxrss is in kilobytes; on macOS in bytes
    return float(usage / 1024.0)

def run_scaling_benchmark(max_qubits: int = 10, shots: int = 1024) -> Dict[str, Any]:
    """
    Executes an Entangled GHZ-type circuit across increasing register sizes.
    Circuit for n qubits: H(0), CNOT(0,1), CNOT(1,2), ..., CNOT(n-2, n-1).
    """
    rows: List[Dict[str, Any]] = []

    print(f"[*] Starting DATA VERSE Quantum Benchmark (2 to {max_qubits} qubits, {shots} shots)...")
    for n in range(2, max_qubits + 1, 2):
        qc = QuantumCircuit(n)
        qc.h(0)
        for i in range(n - 1):
            qc.cx(i, i + 1)

        mem_before = get_memory_usage_mb()
        t0 = time.perf_counter()
        res = qc.run(shots=shots, seed=42)
        elapsed_ms = (time.perf_counter() - t0) * 1000.0
        mem_after = get_memory_usage_mb()

        entry = {
            "num_qubits": n,
            "hilbert_dimension": 1 << n,
            "circuit_depth": res.circuit_depth,
            "gate_count": res.gate_count,
            "shots": shots,
            "execution_time_ms": round(elapsed_ms, 3),
            "memory_usage_mb": round(mem_after, 2)
        }
        rows.append(entry)
        print(f"  - {n} Qubits (dim={1<<n:4d}): {elapsed_ms:7.2f} ms | Mem: {mem_after:.1f} MB")

    # Export to CSV & JSON
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(os.path.dirname(base_dir), "data", "exports")
    os.makedirs(data_dir, exist_ok=True)

    csv_path = os.path.join(data_dir, "benchmark_results.csv")
    json_path = os.path.join(data_dir, "benchmark_results.json")

    with open(csv_path, mode="w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    with open(json_path, mode="w") as f:
        json.dump(rows, f, indent=2)

    return {
        "status": "COMPLETED",
        "csv_path": csv_path,
        "json_path": json_path,
        "data": rows
    }

if __name__ == "__main__":
    run_scaling_benchmark(max_qubits=10, shots=1024)

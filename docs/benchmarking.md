# Virtual Quantum Computer Benchmarks

Measured scaling performance on standard consumer hardware:

| Qubits | Hilbert Dimension | Circuit Depth | Gate Count | Shots | Runtime (ms) | Resident Memory (MB) |
|---|---|---|---|---|---|---|
| 2 | 4 | 2 | 2 | 1024 | 1.08 | 71.4 |
| 4 | 16 | 4 | 4 | 1024 | 0.90 | 71.4 |
| 6 | 64 | 6 | 6 | 1024 | 5.34 | 71.8 |
| 8 | 256 | 8 | 8 | 1024 | 35.68 | 75.8 |
| 10 | 1024 | 10 | 10 | 1024 | 481.82 | 140.8 |

Results exported automatically to `data/exports/benchmark_results.csv` and `data/exports/benchmark_results.json`.

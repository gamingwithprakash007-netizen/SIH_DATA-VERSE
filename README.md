# DATA VERSE: Quantum-Inspired Digital Signature Security & Threat Detection

**SIH Problem Statement**: SIH26141  
**Classification**: Quantum-Information-Based Digital Signature Research Prototype & Cybersecurity Platform  
**Status**: Complete Working Research Prototype

---

## 1. Project Overview & Scientific Positioning

DATA VERSE is a research-oriented software platform that combines classical cryptographic verification, a custom software-based Virtual Quantum Computer, quantum-information protocols, statistical measurement analysis, and controlled cyber-attack simulation to investigate enhanced digital-document signature verification and threat detection.

> **Crucial Disclaimer**:
> This is a **software simulation and research prototype**. We have **not** built physical quantum hardware. The Virtual Quantum Computer is an exact classical simulation of quantum states and circuit evolution written from mathematical first principles in Python and NumPy. Cirq and QSim serve as external validation and reference environments.

---

## 2. Platform Architecture

```
                    DATA VERSE
                        |
              +---------+---------+
              |                   |
              v                   v
        Web Dashboard          REST API
      (Cybersecurity UI)      (FastAPI)
              |                   |
              +---------+---------+
                        |
                        v
               Verification Engine
                        |
          +-------------+-------------+
          |                           |
          v                           v
 Classical Security Layer      Quantum Security Layer
          |                           |
          +--> SHA-256 / SHA3-256     +--> Virtual Quantum Computer
          +--> ECDSA (SECP256R1)      +--> Bell States & Entanglement
          +--> Replay & Nonce Ledger  +--> Teleportation & Pauli Corrections
                                      +--> Statistical Engine (TVD, Chi2)
                                      |
                                      v
                            Threat Scoring Engine
                         (Explainable Weighted Score)
                                      |
                      +---------------+---------------+
                      |               |               |
                      v               v               v
                    SAFE         SUSPICIOUS        ATTACK
```

---

## 3. Implemented Subsystems

1. **Virtual Quantum Computer**: Pure state-vector engine in $\mathbb{C}^{2^n}$ supporting single-qubit ($X, Y, Z, H, S, T, R_x, R_y, R_z$) and multi-qubit ($CNOT, CZ, SWAP$) gates, circuit depth tracking, Born rule projective measurements, and stochastic channel noise models (bit-flip, phase-flip, depolarizing, readout error).
2. **Bell States & Entanglement Engine**: Canonical preparation and correlation expectation measurement for $|\Phi^+\rangle, |\Phi^-\rangle, |\Psi^+\rangle, |\Psi^-\rangle$.
3. **Quantum Teleportation**: 3-qubit Bennett et al. protocol with Alice's Bell-basis measurement and Bob's conditional Pauli corrections ($Z^{m_0} X^{m_1}$).
4. **Classical Cryptography Baseline**: Dual-hashing with SHA-256 and SHA3-256 document fingerprints, paired with ECDSA (SECP256R1 / NIST P-256) signatures.
5. **Quantum Digital Signature (QDS) Research Protocol**: Cryptographically binds document fingerprints with entangled quantum states, generating structured verification packages.
6. **Replay Protection**: Nonce ledger and session window validation detecting duplicate packages, expired sessions, and reused tokens.
7. **Controlled Attack Simulation Laboratory**: Deterministic reproduction of:
   - Normal verification
   - Document tampering (byte alterations)
   - Signature tampering (corrupted signature strings)
   - Forgery simulation (signing with rogue unauthorized keys)
   - Replay attacks (reusing recorded tokens)
   - Quantum channel noise (depolarizing decoherence)
   - Measurement manipulation (statistical readout bias)
8. **Statistical & Threat Scoring Engine**: Computes Total Variation Distance (TVD), Chi-Square goodness-of-fit, and relative entropy to generate an explainable threat score ($0.0 - 100.0$) mapping to `SAFE`, `SUSPICIOUS`, or `ATTACK`.
9. **Forensic Reporting & Audit Persistence**: SQLite audit logs with export to structured JSON and formatted PDF via ReportLab.
10. **REST API & Web UI**: FastAPI backend with OpenAPI documentation (`/docs`) and responsive dark cybersecurity dashboard.

---

## 4. Running the Platform

### Start the Server
```bash
python3 run.py
```
- Web Dashboard: `http://localhost:8000/`
- Interactive API Documentation: `http://localhost:8000/docs`

### Run Automated Unit and Integration Tests
```bash
python3 run_all_tests.py
```

### Run Benchmarking Suite
```bash
python3 benchmarks/benchmark_engine.py
```

### Run the 4 Built-In Demonstration Scenarios
```bash
python3 examples/demo_scenario.py
```

---

## 5. Demonstration Results Summary

| Demo Case | Injected Condition | Expected Verdict | Observed Verdict | Threat Score | Contributing Signal |
|---|---|---|---|---|---|
| **DEMO 1** | Authentic Document & Valid QDS | ACCEPTED | **SAFE** | 1.25 / 100 | Nominal Cryptography & Teleportation |
| **DEMO 2** | 1-Byte Document Tampering | REJECTED | **ATTACK** | 80.62 / 100 | Hash Mismatch Detected |
| **DEMO 3** | Reused Cryptographic Nonce | REJECTED | **ATTACK** | 51.64 / 100 | Nonce Replay Triggered |
| **DEMO 4** | 35% Depolarizing Channel Noise | NOMINAL | **SAFE/SUSPICIOUS** | 0.94 / 100 | Statistical Deviation Tracked |

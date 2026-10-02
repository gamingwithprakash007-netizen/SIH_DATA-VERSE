# Quantum Digital Signature Research Protocol

## 1. Protocol Participants
- **Signer (Alice)**: Possesses document $D$ and private signing key $SK$.
- **Verifier (Bob)**: Receives signed document, public key $PK$, and quantum verification metadata.

## 2. Signing Phase
1. Alice computes document fingerprint $H = \text{SHA-256}(D)$.
2. Alice generates an ECDSA signature $\sigma = \text{Sign}_{SK}(H)$.
3. Alice runs the Virtual Quantum Computer to generate an entangled Bell state $|\Phi^+\rangle$ and records baseline correlation and teleportation fidelity telemetry.
4. Alice generates session ID, fresh cryptographic nonce $N$, and binds all metadata into the Signature Package.

## 3. Verification Phase
1. Bob recomputes $H' = \text{SHA-256}(D)$ and checks $H' == H$.
2. Bob verifies ECDSA signature $\text{Verify}_{PK}(H', \sigma)$.
3. Bob checks the Replay Ledger: verifies $N$ is novel and session is unexpired.
4. Bob executes quantum verification on the Virtual Quantum Computer, measuring correlations and comparing distributions via TVD and Chi-Square.
5. Bob inputs all metrics to the Threat Scoring Engine for final verdict (SAFE / SUSPICIOUS / ATTACK).

# Attack Simulation Laboratory

The Attack Lab provides 7 deterministic scenarios:
1. **NORMAL**: Legitimate document and signature package (Expected: SAFE).
2. **DOCUMENT_TAMPERING**: 1-byte alteration in document payload (Expected: ATTACK).
3. **SIGNATURE_TAMPERING**: Corrupted signature string (Expected: ATTACK).
4. **FORGERY_SIMULATION**: Document signed under rogue unauthenticated keypair (Expected: ATTACK).
5. **REPLAY_ATTACK**: Re-submission of previously verified nonce and session ID (Expected: ATTACK).
6. **QUANTUM_CHANNEL_NOISE**: Stochastic depolarizing channel noise injection (Expected: Increased TVD / Anomaly Score).
7. **MEASUREMENT_MANIPULATION**: Artificial statistical readout biasing (Expected: Low Chi-Square p-value).

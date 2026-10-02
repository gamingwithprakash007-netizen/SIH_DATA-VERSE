# REST API Reference

Exposed via FastAPI at `http://localhost:8000`:
- `POST /documents/upload`: Upload file and generate SHA-256 / SHA3-256 fingerprints.
- `POST /sign`: Sign document using ECDSA + Quantum telemetry.
- `POST /verify`: Execute 18-step verification pipeline.
- `POST /quantum/run`: Execute arbitrary quantum circuits.
- `POST /quantum/bell-state`: Analyze Bell state entanglement and correlations.
- `POST /quantum/teleport`: Execute 3-qubit teleportation with Pauli correction.
- `POST /attacks/*`: Simulate tampering, forgery, replay, noise, manipulation.
- `GET /history`: List recent verification audit records.
- `GET /reports/{id}/pdf`: Download formatted forensic PDF verification report.
- `GET /system/status`: Platform health and configuration.
- `GET /docs`: Interactive Swagger / OpenAPI documentation.

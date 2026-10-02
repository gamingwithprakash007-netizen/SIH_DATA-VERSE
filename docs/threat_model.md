# Cybersecurity Threat Model & Explainable Scoring

## 1. Security Indicators
The Threat Engine computes an explainable composite threat score $T \in [0.0, 100.0]$:
$$T = w_1 A_{\text{hash}} + w_2 A_{\text{sig}} + w_3 A_{\text{meas}} + w_4 A_{\text{sess}} + w_5 A_{\text{replay}}$$

Default configurable weights:
- $w_1 = 0.40$ (Document Hash Anomaly)
- $w_2 = 0.40$ (Digital Signature Anomaly)
- $w_3 = 0.20$ (Quantum Measurement Statistical Anomaly)
- $w_4 = 0.15$ (Session Inconsistency Anomaly)
- $w_5 = 0.35$ (Replay Attack Anomaly)

## 2. Classification Thresholds
- **SAFE**: $T < 15.0$
- **SUSPICIOUS**: $15.0 \le T < 35.0$
- **ATTACK**: $T \ge 35.0$

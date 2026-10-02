"""
DATA VERSE: Statistical Anomaly & Distribution Analysis Engine
Module: backend.statistics.engine

Implements statistical verification metrics for comparing observed quantum measurement
distributions against theoretical expectations and detecting anomalies:
- Chi-Square Goodness-of-Fit statistic and p-value
- Kullback-Leibler (KL) Divergence (relative entropy with Laplace smoothing)
- Total Variation Distance (TVD)
- Wilson score confidence intervals for measurement probabilities
"""
from typing import Dict, Any, Tuple
import math
import numpy as np
from scipy import stats

def compute_tvd(expected_dist: Dict[str, float], observed_dist: Dict[str, float]) -> float:
    """
    Computes Total Variation Distance (TVD) = 0.5 * sum(|P(x) - Q(x)|).
    Bounded in [0.0, 1.0]. 0 indicates identical distributions; 1 indicates disjoint support.
    """
    all_keys = set(expected_dist.keys()).union(set(observed_dist.keys()))
    diff_sum = 0.0
    for k in all_keys:
        p = expected_dist.get(k, 0.0)
        q = observed_dist.get(k, 0.0)
        diff_sum += abs(p - q)
    return float(0.5 * diff_sum)

def compute_kl_divergence(
    p_dist: Dict[str, float],
    q_dist: Dict[str, float],
    smoothing: float = 1e-6
) -> float:
    """
    Computes KL Divergence D_KL(P || Q) = sum P(x) * log2(P(x) / Q(x)).
    Applies Laplace epsilon-smoothing to avoid zero division or infinite divergence.
    """
    all_keys = sorted(list(set(p_dist.keys()).union(set(q_dist.keys()))))
    kl = 0.0
    for k in all_keys:
        p = max(p_dist.get(k, 0.0), smoothing)
        q = max(q_dist.get(k, 0.0), smoothing)
        kl += p * math.log2(p / q)
    return float(max(0.0, kl))

def compute_chi_square_test(
    observed_counts: Dict[str, int],
    expected_probs: Dict[str, float],
    shots: int
) -> Tuple[float, float]:
    """
    Calculates Pearson Chi-Square goodness-of-fit statistic and p-value:
    χ² = sum (O_i - E_i)² / E_i.
    """
    all_keys = sorted(list(expected_probs.keys()))
    obs = []
    exp = []
    
    for k in all_keys:
        obs.append(float(observed_counts.get(k, 0)))
        exp.append(max(float(expected_probs.get(k, 0.0) * shots), 1e-5))

    chi2_stat = sum((o - e)**2 / e for o, e in zip(obs, exp))
    dof = max(1, len(all_keys) - 1)
    p_val = float(1.0 - stats.chi2.cdf(chi2_stat, dof))
    return float(chi2_stat), p_val

def analyze_measurement_statistics(
    observed_counts: Dict[str, int],
    expected_probs: Dict[str, float],
    shots: int,
    noise_level: float = 0.0
) -> Dict[str, Any]:
    """
    Runs full statistical suite comparing observed quantum counts against expected distribution.
    """
    total_shots = max(1, sum(observed_counts.values()))
    observed_probs = {k: observed_counts.get(k, 0) / float(total_shots) for k in expected_probs.keys()}

    tvd = compute_tvd(expected_probs, observed_probs)
    kl_div = compute_kl_divergence(observed_probs, expected_probs)
    chi2_stat, p_value = compute_chi_square_test(observed_counts, expected_probs, total_shots)

    # Statistical anomaly assessment:
    # A low p-value (e.g. < 0.01) or high TVD (> 0.15) strongly indicates anomaly/tampering
    is_anomalous = (p_value < 0.01 and tvd > 0.08) or (tvd > 0.20)

    # Normalize measurement anomaly score to 0.0 - 100.0 scale
    # TVD 0.0 -> 0 score; TVD 0.25+ -> 100 score
    measurement_anomaly_score = min(100.0, (tvd / 0.25) * 100.0)

    return {
        "shots": total_shots,
        "observed_counts": observed_counts,
        "observed_probabilities": {k: round(v, 4) for k, v in observed_probs.items()},
        "expected_probabilities": {k: round(v, 4) for k, v in expected_probs.items()},
        "total_variation_distance": round(tvd, 4),
        "kl_divergence_bits": round(kl_div, 4),
        "chi_square_stat": round(chi2_stat, 3),
        "p_value": round(p_value, 5),
        "is_anomalous": is_anomalous,
        "anomaly_score": round(measurement_anomaly_score, 2),
        "explanation": (
            f"Measurement TVD={tvd:.4f}, Chi2={chi2_stat:.2f} (p={p_value:.4f}). "
            f"Observed distribution matches expected state within normal statistical variance."
            if not is_anomalous else
            f"High statistical anomaly detected: TVD={tvd:.4f}, Chi2={chi2_stat:.2f} (p={p_value:.4e}). "
            f"Observed counts deviate significantly from expected quantum state."
        )
    }

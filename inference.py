"""
inference.py -- M node (ITU-T Y.3172 pipeline)

Baseline pulse-presence classifier. This is an interpretable, rule-based
baseline (not a trained neural network) so the reference pipeline is
transparent and auditable for the hackathon submission -- see
docs/model_card.md for intended use, limitations, and evaluation plan.

Swapping in a trained model (e.g. gradient-boosted trees on labeled
waveform features) is a drop-in replacement: it must accept `Features`
and return a `PulsePrediction` to remain compatible with policy.py.
"""

from __future__ import annotations

from dataclasses import dataclass

from .preprocessing import Features


@dataclass
class PulsePrediction:
    probability: float   # 0-1, estimated probability a true pulse is present
    signal_quality: float


def predict(features: Features) -> PulsePrediction:
    """Estimate pulse-presence probability from extracted features.

    Baseline heuristic (documented, not hidden):
      - No peaks detected at all -> very low probability (flatline case).
      - Peaks present -> probability scales with signal quality and a
        plausible physiological interval (0.33s-1.5s, i.e. 40-180bpm).
    """
    if features.peak_count == 0 or features.mean_peak_interval_s is None:
        # No plausible cardiac pattern found. If the trace itself is clean
        # (good contact), this is a confident "no pulse" reading; if the
        # trace is noisy, policy.py's quality gate will override this to
        # "uncertain" regardless of how low this probability is.
        probability = 0.05
    else:
        interval = features.mean_peak_interval_s
        physiological = 0.33 <= interval <= 1.5
        base = 0.55 + 0.4 * features.signal_quality
        probability = base if physiological else base * 0.4

    probability = max(0.0, min(1.0, probability))
    return PulsePrediction(probability=round(probability, 3), signal_quality=features.signal_quality)

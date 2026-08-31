"""
capture.py -- SRC node (ITU-T Y.3172 pipeline)

Represents the sensor source: a disposable adhesive skin-patch PPG sensor
sited over a guideline-recommended central pulse site (carotid for adults
and children 1yr-puberty, brachial for infants under 1yr), wired to a
bedside collector.

This module does NOT talk to real hardware. It provides:
  1. A typed Waveform container with capture metadata.
  2. A synthetic waveform generator used by the demo and tests, standing in
     for the sensor during the prototype stage (see docs/model_card.md).

Replacing `generate_synthetic_waveform` with a real ADC/BLE read is the
only change needed to go from prototype to bench-hardware demo -- nothing
downstream (preprocessing, inference, policy) needs to know the source.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum

import numpy as np


class PulseSite(str, Enum):
    CAROTID = "carotid"   # adults, children 1yr-puberty (lateral neck, below jaw)
    BRACHIAL = "brachial"  # infants under 1yr (medial upper arm)


class SignalCondition(str, Enum):
    CLEAN = "clean"
    NOISY = "noisy"
    FLATLINE = "flatline"   # simulates true pulse-not-detected


@dataclass
class Waveform:
    samples: np.ndarray
    sample_rate_hz: int
    site: PulseSite
    captured_at: float = field(default_factory=time.time)
    device_id: str = "PS-SIM-0001"

    @property
    def duration_s(self) -> float:
        return len(self.samples) / self.sample_rate_hz


def generate_synthetic_waveform(
    condition: SignalCondition = SignalCondition.CLEAN,
    site: PulseSite = PulseSite.CAROTID,
    duration_s: float = 5.0,
    sample_rate_hz: int = 100,
    heart_rate_bpm: float = 78.0,
    seed: int | None = None,
) -> Waveform:
    """Generate a synthetic pulse waveform for demo/testing.

    This stands in for the SRC sensor during the prototype stage. Real
    waveforms are never fabricated for clinical claims -- this is clearly
    labeled synthetic data (see data/sample/README.md).
    """
    rng = np.random.default_rng(seed)
    n = int(duration_s * sample_rate_hz)
    t = np.linspace(0, duration_s, n, endpoint=False)

    hr_hz = heart_rate_bpm / 60.0
    base = np.sin(2 * np.pi * hr_hz * t) ** 3  # peaky pulse-like shape

    if condition == SignalCondition.CLEAN:
        noise = rng.normal(0, 0.03, n)
        signal = base + noise

    elif condition == SignalCondition.NOISY:
        motion_artifact = 0.6 * np.sin(2 * np.pi * 2.3 * t + rng.uniform(0, 6))
        noise = rng.normal(0, 0.25, n)
        signal = 0.5 * base + motion_artifact + noise

    elif condition == SignalCondition.FLATLINE:
        noise = rng.normal(0, 0.02, n)
        signal = noise  # no cardiac component: true "pulse not detected"

    else:
        raise ValueError(f"Unknown condition: {condition}")

    return Waveform(samples=signal, sample_rate_hz=sample_rate_hz, site=site)

"""
preprocessing.py -- PP node (ITU-T Y.3172 pipeline)

Filters the raw waveform, estimates a signal-quality score, and extracts
the small feature set the M (model) node consumes.

Signal quality here measures *contact/noise quality* (how smooth and
low-artifact the trace is) -- deliberately independent of whether a
cardiac peak pattern is present. A well-attached patch reading a genuine
flatline is high quality (confidently no pulse); a poorly-attached patch
during motion is low quality regardless of any spurious peaks it produces
(forces the "uncertain" policy branch -- see src/policy.py).

Kept deliberately simple and dependency-light (numpy only) so the pipeline
is easy to audit end-to-end for the hackathon submission -- see
docs/architecture.md for how this maps to the readiness/control
requirements (reproducible preprocessing, data minimisation).
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .capture import Waveform

# Empirically-set normalizing scale for the jitter->quality mapping (see
# docs/model_card.md "Evaluation" for how this would be calibrated against
# real waveform data rather than fixed by hand).
JITTER_NORMALIZATION_SCALE = 0.15


@dataclass
class Features:
    signal_quality: float       # 0-1, higher is better (contact/noise quality)
    peak_count: int
    mean_peak_interval_s: float | None
    amplitude_std: float


def _bandpass_moving_average(samples: np.ndarray, window: int = 5) -> np.ndarray:
    """Lightweight band-pass stand-in: smooths high-frequency noise while
    preserving the pulse envelope. A real deployment would use a proper
    Butterworth band-pass (0.5-8 Hz); this keeps the reference pipeline
    dependency-free for the prototype."""
    if len(samples) < window:
        return samples
    kernel = np.ones(window) / window
    return np.convolve(samples, kernel, mode="same")


def _signal_quality(raw: np.ndarray) -> float:
    """Sample-to-sample jitter as a proxy for contact/motion noise.
    Low jitter = smooth trace = high quality, whether or not it turns out
    to contain a heartbeat."""
    jitter = float(np.mean(np.abs(np.diff(raw))))
    quality = 1.0 - min(jitter / JITTER_NORMALIZATION_SCALE, 1.0)
    return round(max(0.0, quality), 3)


# Absolute amplitude floor a candidate peak must clear, in the same units
# as the (simulated) sensor signal. This is what actually separates "no
# cardiac component" (flatline noise stays near zero) from a real beat,
# independent of the trace's own noise floor -- a purely relative
# threshold (mean + k*std) finds "peaks" in pure noise too.
ABS_PEAK_FLOOR = 0.15


def _find_peaks(samples: np.ndarray, sample_rate_hz: int) -> np.ndarray:
    """Local-maxima peak detector: a candidate must clear both a
    dynamic, trace-relative threshold and an absolute amplitude floor
    (so a quiet flatline trace can't produce spurious "peaks" just
    because they're locally above its own noise), with a refractory
    period so one beat isn't double-counted."""
    threshold = max(samples.mean() + 0.5 * samples.std(), ABS_PEAK_FLOOR)
    refractory = int(0.25 * sample_rate_hz)  # 250ms, ~240bpm ceiling

    peaks = []
    last_peak = -refractory
    for i in range(1, len(samples) - 1):
        if (
            samples[i] > threshold
            and samples[i] > samples[i - 1]
            and samples[i] >= samples[i + 1]
            and (i - last_peak) >= refractory
        ):
            peaks.append(i)
            last_peak = i
    return np.array(peaks)


def preprocess(waveform: Waveform) -> tuple[Features, np.ndarray]:
    """Filter the waveform and extract features for the M node.

    Returns (features, filtered_samples) -- the filtered trace is kept
    for display/logging (see src/logging_.py), features feed inference.
    """
    filtered = _bandpass_moving_average(waveform.samples)
    peaks = _find_peaks(filtered, waveform.sample_rate_hz)
    signal_quality = _signal_quality(waveform.samples)

    if len(peaks) >= 2:
        intervals = np.diff(peaks) / waveform.sample_rate_hz
        mean_interval = float(np.mean(intervals))
    else:
        mean_interval = None

    features = Features(
        signal_quality=signal_quality,
        peak_count=len(peaks),
        mean_peak_interval_s=mean_interval,
        amplitude_std=round(float(np.std(filtered)), 4),
    )
    return features, filtered

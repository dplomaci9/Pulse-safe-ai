"""
policy.py -- P node (ITU-T Y.3172 pipeline)

Translates the model's probability into one of three advisory states and
applies the safety guardrails described in the technical report:
  - Conservative thresholds (never overconfident).
  - An explicit "uncertain" state when signal quality is poor.
  - Mandatory human confirmation is enforced by the caller (src/demo /
    the bedside UI), never bypassed here -- this module only advises.

PulseSafe AI is decision support, not autonomous resuscitation. It never
declares death and never starts or stops CPR.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .inference import PulsePrediction

MIN_SIGNAL_QUALITY = 0.45          # below this, force "uncertain" regardless of probability
PRESENT_THRESHOLD = 0.65           # probability >= this -> "pulse likely present"
NOT_DETECTED_THRESHOLD = 0.20      # probability <= this (with good signal) -> "pulse not detected"


class AdvisoryState(str, Enum):
    LIKELY_PRESENT = "Pulse likely present"
    NOT_DETECTED = "Pulse not detected"
    UNCERTAIN = "Uncertain — use clinical judgment"


@dataclass
class Advisory:
    state: AdvisoryState
    confidence_pct: float
    reason: str


def advise(prediction: PulsePrediction) -> Advisory:
    """Apply policy thresholds to produce a three-state advisory.

    Always requires human confirmation downstream -- see docs/model_card.md
    "Guardrail statement" and Scenario 2 in docs/risk_register.md.
    """
    confidence_pct = round(prediction.probability * 100, 1)

    if prediction.signal_quality < MIN_SIGNAL_QUALITY:
        return Advisory(
            state=AdvisoryState.UNCERTAIN,
            confidence_pct=confidence_pct,
            reason=f"Signal quality {prediction.signal_quality:.2f} below minimum "
                   f"{MIN_SIGNAL_QUALITY}; standard clinical assessment required.",
        )

    if prediction.probability >= PRESENT_THRESHOLD:
        return Advisory(
            state=AdvisoryState.LIKELY_PRESENT,
            confidence_pct=confidence_pct,
            reason="Probability and signal quality both above threshold.",
        )

    if prediction.probability <= NOT_DETECTED_THRESHOLD:
        return Advisory(
            state=AdvisoryState.NOT_DETECTED,
            confidence_pct=confidence_pct,
            reason="Probability at/below not-detected threshold with adequate signal quality.",
        )

    return Advisory(
        state=AdvisoryState.UNCERTAIN,
        confidence_pct=confidence_pct,
        reason="Probability falls in the ambiguous zone between thresholds.",
    )

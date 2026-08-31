"""
logging_.py -- D (Distributor) and SINK nodes (ITU-T Y.3172 pipeline)

Every pulse-check event is time-stamped and logged with the waveform
summary, model output, and policy advisory, so the human decision can be
recorded next to it (see docs/architecture.md, node P: "human-in-loop,
no autonomous action, incident and audit policy").

Named `logging_` (trailing underscore) to avoid shadowing Python's
built-in `logging` module.
"""

from __future__ import annotations

import json
import time
from dataclasses import asdict, dataclass
from pathlib import Path

from .capture import Waveform
from .inference import PulsePrediction
from .policy import Advisory


@dataclass
class EventRecord:
    timestamp: float
    device_id: str
    site: str
    signal_quality: float
    probability: float
    advisory_state: str
    advisory_reason: str
    human_decision: str | None = None   # filled in when the team confirms/overrides
    override_reason: str | None = None


def build_record(waveform: Waveform, prediction: PulsePrediction, advisory: Advisory) -> EventRecord:
    return EventRecord(
        timestamp=waveform.captured_at,
        device_id=waveform.device_id,
        site=waveform.site.value,
        signal_quality=prediction.signal_quality,
        probability=prediction.probability,
        advisory_state=advisory.state.value,
        advisory_reason=advisory.reason,
    )


def append_event(record: EventRecord, log_path: str | Path = "pulsesafe_events.jsonl") -> None:
    """Append one event as a JSON line -- append-only, so the audit trail
    is never silently rewritten. A real deployment would write to a
    governed, access-controlled store per docs/architecture.md (SINK row:
    SDAIA Personal Data Protection Law; MoH clinical/health-information
    policy)."""
    path = Path(log_path)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(asdict(record)) + "\n")


def confirm(record: EventRecord, human_decision: str, override_reason: str | None = None) -> EventRecord:
    """Record the team's final decision against an event. The advisory is
    never auto-applied -- this call is how a human confirmation or
    override enters the audit log."""
    record.human_decision = human_decision
    record.override_reason = override_reason
    return record

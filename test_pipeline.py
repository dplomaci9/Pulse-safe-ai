"""
test_pipeline.py -- unit tests for the SRC -> PP -> M -> P pipeline.

Run with: pytest -v
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.capture import PulseSite, SignalCondition, generate_synthetic_waveform
from src.preprocessing import preprocess
from src.inference import predict
from src.policy import Advisory, AdvisoryState, advise, PulsePrediction


def _run_pipeline(condition: SignalCondition, seed: int) -> Advisory:
    waveform = generate_synthetic_waveform(condition=condition, seed=seed)
    features, _ = preprocess(waveform)
    prediction = predict(features)
    return advise(prediction)


def test_clean_signal_reads_present():
    advisory = _run_pipeline(SignalCondition.CLEAN, seed=42)
    assert advisory.state == AdvisoryState.LIKELY_PRESENT


def test_noisy_signal_reads_uncertain():
    advisory = _run_pipeline(SignalCondition.NOISY, seed=7)
    assert advisory.state == AdvisoryState.UNCERTAIN


def test_flatline_reads_not_detected():
    advisory = _run_pipeline(SignalCondition.FLATLINE, seed=1)
    assert advisory.state == AdvisoryState.NOT_DETECTED


def test_infant_brachial_site_present():
    waveform = generate_synthetic_waveform(condition=SignalCondition.CLEAN, site=PulseSite.BRACHIAL, seed=99)
    features, _ = preprocess(waveform)
    prediction = predict(features)
    advisory = advise(prediction)
    assert advisory.state == AdvisoryState.LIKELY_PRESENT
    assert waveform.site == PulseSite.BRACHIAL


def test_low_quality_forces_uncertain_regardless_of_probability():
    """Policy guardrail: even a high-probability reading must be
    downgraded to 'uncertain' if signal quality is below the minimum."""
    prediction = PulsePrediction(probability=0.95, signal_quality=0.1)
    advisory = advise(prediction)
    assert advisory.state == AdvisoryState.UNCERTAIN
    assert "quality" in advisory.reason.lower()


def test_policy_never_returns_autonomous_action():
    """PulseSafe AI is advisory-only: confirm the three defined states
    are the entire output space (no 'stop CPR' / 'confirm death' etc.)."""
    valid_states = {AdvisoryState.LIKELY_PRESENT, AdvisoryState.NOT_DETECTED, AdvisoryState.UNCERTAIN}
    for condition in [SignalCondition.CLEAN, SignalCondition.NOISY, SignalCondition.FLATLINE]:
        advisory = _run_pipeline(condition, seed=123)
        assert advisory.state in valid_states


def test_event_logging_round_trip(tmp_path):
    from src.logging_ import append_event, build_record, confirm

    waveform = generate_synthetic_waveform(condition=SignalCondition.CLEAN, seed=42)
    features, _ = preprocess(waveform)
    prediction = predict(features)
    advisory = advise(prediction)

    record = build_record(waveform, prediction, advisory)
    record = confirm(record, human_decision="confirmed present", override_reason=None)

    log_file = tmp_path / "events.jsonl"
    append_event(record, log_file)

    assert log_file.exists()
    content = log_file.read_text()
    assert "confirmed present" in content
    assert waveform.site.value in content

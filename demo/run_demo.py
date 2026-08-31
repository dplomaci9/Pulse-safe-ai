#!/usr/bin/env python3
"""
run_demo.py -- End-to-end PulseSafe AI pipeline demo.

Runs three scripted scenarios (clean / noisy / uncertain / flatline)
through the full SRC -> PP -> M -> P -> D pipeline and prints the
three-state advisory with latency, matching the "Live software" scene of
the demo video storyboard.

Usage:
    python demo/run_demo.py
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.capture import PulseSite, SignalCondition, generate_synthetic_waveform
from src.preprocessing import preprocess
from src.inference import predict
from src.policy import advise
from src.logging_ import build_record, append_event

SCENARIOS = [
    ("Clean signal, adult carotid site", SignalCondition.CLEAN, PulseSite.CAROTID, 42),
    ("Noisy / motion-artifact signal", SignalCondition.NOISY, PulseSite.CAROTID, 7),
    ("No cardiac component (pulse not detected)", SignalCondition.FLATLINE, PulseSite.CAROTID, 1),
    ("Infant, brachial site, clean signal", SignalCondition.CLEAN, PulseSite.BRACHIAL, 99),
]

LOG_PATH = Path(__file__).resolve().parent / "demo_events.jsonl"


def run_scenario(label: str, condition: SignalCondition, site: PulseSite, seed: int) -> None:
    start = time.perf_counter()

    waveform = generate_synthetic_waveform(condition=condition, site=site, seed=seed)
    features, _filtered = preprocess(waveform)
    prediction = predict(features)
    advisory = advise(prediction)

    latency_ms = (time.perf_counter() - start) * 1000

    record = build_record(waveform, prediction, advisory)
    append_event(record, LOG_PATH)

    print(f"\n=== {label} ===")
    print(f"  site:            {site.value}")
    print(f"  signal quality:  {features.signal_quality:.2f}")
    print(f"  peaks detected:  {features.peak_count}")
    print(f"  advisory:        {advisory.state.value}")
    print(f"  confidence:      {advisory.confidence_pct}%")
    print(f"  reason:          {advisory.reason}")
    print(f"  latency:         {latency_ms:.1f} ms")
    print(f"  --> mandatory human confirmation required before any action")


def main() -> None:
    print("PulseSafe AI -- reference pipeline demo")
    print("Decision support only. Never declares death. Never starts/stops CPR.")
    print(f"Events logged to: {LOG_PATH}")

    for label, condition, site, seed in SCENARIOS:
        run_scenario(label, condition, site, seed)

    print("\nDone. See demo_events.jsonl for the full audit trail of this run.")


if __name__ == "__main__":
    main()

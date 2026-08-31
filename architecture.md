# Architecture — ITU-T Y.3172 pipeline mapping

PulseSafe AI maps onto the ITU-T Y.3172 machine-learning pipeline (SRC, C, PP, M, P, D,
SINK). This mirrors Section 3 of the technical report; code references point to where
each node is actually implemented in this repository.

| Node | Use case | Implementation | Readiness / control requirement |
|---|---|---|---|
| **SRC** | Disposable adhesive skin-patch PPG sensor with a wired/short-range-wireless connector to the bedside monitor; sited over the **carotid** (adults/children 1yr–puberty, lateral neck, below the jaw) or **brachial** (infants under 1yr, medial upper arm) pulse, per AHA/ILCOR 2025 central-pulse-check-site guidance | `src/capture.py` | Device usability & age-stratified safe-placement SOP; AHA/ILCOR 2025 central-pulse-check-site guidance; provenance and calibration guidelines |
| **C** | Bedside monitor, tablet, or microcontroller aggregating sensor data with timestamp and team metadata | `src/capture.py::Waveform` (metadata fields) | Reliability/availability guidelines for edge platforms; secure-collection and failure-detection requirements |
| **PP** | Band-pass filtering, artifact detection, pause-window segmentation, normalization | `src/preprocessing.py` | Reproducible-preprocessing standards; data-minimisation guidance |
| **M** | Baseline classifier estimating probability of true pulse presence, run in a sandbox before deployment | `src/inference.py` | Benchmarking standards; held-out validation and subgroup-analysis guidance; SDAIA AI Ethics Principles |
| **P** | Confidence thresholds, uncertain-zone rules, mandatory human confirmation before any action is taken | `src/policy.py` | Human-in-loop and overriding-conditions policy; incident/audit-trail requirements |
| **D** | Bedside display plus a secure, role-based quality-improvement dashboard hosted on hospital/cloud infrastructure | `src/logging_.py` | Energy and compute-resource considerations; role-based access control |
| **SINK** | Code blue team and hospital quality-improvement / governance system | `src/logging_.py::confirm` (records the human decision) | SDAIA Personal Data Protection Law; MoH clinical and health-information policy |

## Why sensor placement follows AHA/ILCOR guidance, not a peripheral site

Peripheral sites (finger, wrist) become unreliable during the low-flow states seen in
CPR. The patch is sited over a guideline-recommended **central** pulse:

- **Carotid** (lateral neck, below the jaw) — adults and children 1 year to puberty.
- **Brachial** (medial upper arm) — infants under 1 year, since infant necks are too
  short to palpate the carotid reliably.

## End-to-end flow

```
SRC (sensor) --> C (collector) --> PP (preprocess) --> M (model)
    --> P (policy: thresholds, uncertain zone) --> D (display/log)
    --> SINK (human decision, audit trail)
```

Concretely, `demo/run_demo.py` calls:

```python
waveform   = generate_synthetic_waveform(...)   # SRC + C
features   = preprocess(waveform)                # PP
prediction = predict(features)                   # M
advisory   = advise(prediction)                  # P
record     = build_record(waveform, prediction, advisory)  # D
append_event(record)                             # D -> SINK (audit log)
```

A human confirmation (`src/logging_.py::confirm`) is a separate, required call —
the pipeline never auto-applies its own advisory.

See the technical report (Section 3, "Mapped documents") for the full readiness/policy
framing of this mapping.

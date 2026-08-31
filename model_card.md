# Model card — PulseSafe AI baseline pulse-presence classifier

## Intended use

Decision *support* for code blue pulse-check events. Produces one of three advisory
states — **Pulse likely present**, **Pulse not detected**, **Uncertain — use clinical
judgment** — displayed alongside a confidence score for a trained clinician to confirm
or override.

## Explicit non-goals / guardrail statement

PulseSafe AI is **not** autonomous. It never:
- Declares death.
- Starts or stops CPR.
- Suppresses or replaces standard manual pulse assessment.

If signal quality is poor, the model is outside its validated population, connectivity
fails, or output confidence is insufficient, the system displays "Uncertain — use
clinical judgment," does not suppress standard assessment, and records the reason
(`src/policy.py`).

## Model description

The current baseline (`src/inference.py::predict`) is an **interpretable, rule-based
classifier** — not a trained neural network — chosen deliberately for the prototype
stage so every decision boundary is auditable:

1. `src/preprocessing.py` extracts a signal-quality score (sample-to-sample jitter,
   independent of whether a heartbeat is present) and a peak/interval pattern from the
   filtered waveform.
2. `src/inference.py` estimates a pulse-presence probability from the peak pattern.
3. `src/policy.py` applies conservative thresholds: signal quality below 0.45 forces
   "Uncertain" **regardless of probability** — the quality gate cannot be bypassed by a
   confident-looking probability score.

Swapping in a trained model (e.g. a gradient-boosted classifier or small CNN on labeled
waveform features) is a drop-in replacement — see `src/inference.py` docstring.

## Training / calibration data

**None yet.** This is a prototype-stage reference pipeline evaluated only on synthetic
waveforms (`data/sample/`). No real patient, volunteer, or clinical waveform data has
been used. The threshold constants in `src/policy.py` and `src/preprocessing.py` are
hand-set for the demo, not learned or clinically calibrated.

## Evaluation plan (not yet executed)

Per the technical report's four-phase plan:

| Phase | Scenario | Measures | Gate |
|---|---|---|---|
| A — Software | Clean/noisy labelled waveform simulations | AUROC/AUPRC, sensitivity, specificity, calibration, latency | Hold if quality gate or latency fails |
| B — Simulation lab | Mock code blue with trained teams | Pulse-check duration, interruption time, agreement, override rate | Proceed only after safety/human-factors review |
| C — Silent prospective | Real workflow, no clinical influence | Missingness, drift, subgroup performance | No advisory use until predefined criteria met |
| D — Controlled clinical validation | Approved protocol and oversight | Clinical performance, safety events | Regulatory/institutional go/no-go |

## Known limitations

- Rule-based baseline, not trained on real physiological data.
- Peak-detection and jitter thresholds are hand-tuned constants (see inline comments in
  `src/preprocessing.py`), not derived from a labeled dataset.
- No subgroup (age, skin tone, perfusion state) validation has been performed — required
  before any deployment claim (see `docs/risk_register.md`, "Bias / performance gap").
- No clinical-effectiveness claim is made anywhere in this repository.

## Contact

See the technical report's title block for team and contact details.

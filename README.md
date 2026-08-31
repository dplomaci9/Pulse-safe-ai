# PulseSafe AI

**AI-Assisted Pulse Verification for Code Blue Resuscitation**
ITU AI Readiness Hackathon — KSA

PulseSafe AI is an advisory pulse-verification assistant for code blue events. During
the brief pulse-check interval, a compact adhesive skin-patch sensor captures a
physiological waveform; an edge ML pipeline filters artifacts and estimates whether a
pulse is likely present, not detected, or uncertain. **It never declares death, starts,
or stops CPR** — it provides a time-stamped second signal, a confidence level, and
requires human confirmation, while creating an auditable quality-improvement record.

This repository contains the reference software pipeline demonstrated in the
submission: simulated waveform capture, preprocessing, a baseline classifier, the
policy/safety layer, and event logging — mapped explicitly to the ITU-T Y.3172 ML
pipeline (SRC → C → PP → M → P → D → SINK).

## Guardrail statement

PulseSafe AI is decision support, not autonomous resuscitation. If signal quality is
poor, the model is outside its validated population, connectivity fails, or output
confidence is insufficient, the system displays "Uncertain — use clinical judgment,"
does not suppress standard assessment, and records the reason.

## Quickstart

```bash
python3 -m venv .venv && source .venv/bin/activate   # optional but recommended
pip install -r requirements.txt

python demo/run_demo.py       # run the four scripted scenarios end to end
pytest tests/ -v               # run the test suite
```

Expected demo output: four scenarios (clean/adult, noisy/adult, flatline/adult,
clean/infant) each producing one of the three advisory states, with latency and a
human-confirmation prompt. Every run appends to `demo/demo_events.jsonl` as an audit
trail.

## Repository structure

```
README.md
src/                  capture (SRC), preprocessing (PP), inference (M),
                      policy (P), logging (D/SINK)
demo/                 run_demo.py — end-to-end scripted walkthrough
data/sample/          synthetic waveform data only (no real patient data)
tests/                pytest unit tests
docs/                 architecture.md, model_card.md, risk_register.md,
                      knowledge_base.md
requirements.txt
LICENSE
```

## Sensor placement

Per AHA/ILCOR 2025 central-pulse-check guidance, the patch is sited over a central
pulse — **carotid** (lateral neck, below the jaw) for adults and children 1 year to
puberty, **brachial** (medial upper arm) for infants under 1 year — not a peripheral
site, since peripheral perfusion becomes unreliable during CPR's low-flow states. See
`docs/architecture.md` for the full rationale.

## Prototype status

This is a hackathon software prototype using **synthetic data only**. It is not
presented as a clinically validated or regulatory-cleared medical device. See
`docs/model_card.md` for intended use, limitations, and the evaluation plan required
before any clinical claim.

## Full submission package

The complete technical report (5-page format), video storyboard, and knowledge base are
in the team's submission package alongside this repository.

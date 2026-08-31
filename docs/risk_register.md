# Risk register

Mirrors the technical report's "Key risks and mitigations" and "Evaluation scenarios."

## Key risks and mitigations

| Risk | Mitigation |
|---|---|
| False negative | Retain standard clinical assessment; display uncertainty; never suppress CPR protocol |
| False positive | Require human confirmation and corroborating clinical/rhythm information; monitor adverse events |
| Motion/noise | Signal-quality gate (`src/policy.py::MIN_SIGNAL_QUALITY`) forces "uncertain" output automatically |
| Automation bias | Training, neutral UI, visible confidence/limitations, mandatory confirmation (`src/logging_.py::confirm`) |
| Privacy breach | Collect minimum data, encrypt, restrict access, separate identifiers, prohibit secondary use (e.g. advertising, profiling) |
| Model drift/bias | Version control, monitoring, subgroup analysis, revalidation, rollback plan |

## Evaluation scenarios and policy response

| Scenario | What is observed | Pre-agreed response |
|---|---|---|
| Successful simulation deployment | Prototype used in a simulation centre; identifies clean signals quickly, returns uncertain during motion, records the team's final decision | Accept only if predefined technical, usability, and safety gates are met; publish model card, limitations, and simulation results; do not imply clinical effectiveness |
| Poor signal or disagreement | Sensor displaced or compressions continue during the window; model returns "Uncertain," team's assessment differs | Clinical protocol prevails; log quality and override reason; notify team leader; review episode; use for retraining only under approved governance |
| Bias or performance gap | Validation shows materially lower performance for a device, population, or perfusion state | Pause deployment for that subgroup; investigate data representation and sensor factors; collect governed data; recalibrate/retrain; repeat independent validation before release |
| Cybersecurity or outage | Connectivity lost or an unauthorised user accesses logs | Fail safely to standard care; suppress stale outputs; isolate affected systems; preserve forensic logs; notify institutional security/privacy officers; root-cause analysis |
| Misuse of inferred health information | A provider uses pulse-check data or inferred clinical signals for advertising, profiling, or unrelated commercial activity | Treat as a privacy and ethics breach: stop the secondary use, preserve evidence, notify governance/privacy authorities, assess affected individuals, delete or segregate unlawfully used data, impose contractual and technical controls |
| Successful scale-up | Multiple hospitals request deployment; infrastructure and staffing differ | Readiness gate per site: connectivity, device calibration, trained users, data governance, incident response, equity review; deploy first in sandbox/simulation |

## Decision rights

- **Clinician / team leader** — final patient-care decision and override.
- **Product safety owner** — model release, rollback, and risk acceptance within governance.
- **Hospital governance/privacy/security** — data use, incident response, and deployment approval.
- **Independent evaluator** — validation, subgroup analysis, and readiness evidence.

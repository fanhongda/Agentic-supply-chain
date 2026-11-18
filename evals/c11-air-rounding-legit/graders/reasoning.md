---
type: llm
weight: 2
---

Judge only the text below, which audits an air freight invoice.

PASS if it accepts the billed weight of 52.5 kg as the correct round-up of the 52.25 kg
volumetric weight to the 0.5 kg billing increment.
FAIL if it treats the 0.25 kg difference as an overcharge or discrepancy, or if it says
the chargeable weight should have been 52.25 kg or 50.0 kg.

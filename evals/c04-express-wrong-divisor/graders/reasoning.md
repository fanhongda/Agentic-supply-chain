---
type: llm
weight: 2
---

Judge only the text below, which audits an express freight invoice.

PASS if it says the billed weight is too high because the carrier used a volumetric
divisor of 5000 where the contract specifies 6000, and gives 20.0 kg as the correct
chargeable weight.
FAIL if it accepts 24.0 kg as the correct chargeable weight, or if it questions the
weight without naming the divisor as the cause.

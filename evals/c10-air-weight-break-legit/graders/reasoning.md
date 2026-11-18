---
type: llm
weight: 2
---

Judge only the text below, which audits an air freight invoice.

PASS if it accepts the billed weight of 100.0 kg as legitimate even though the chargeable
weight is 95.0 kg, because 100 kg at the 100 kg break costs 350.00 while 95 kg at the
45 kg break would cost 399.00.
FAIL if it treats the 100.0 kg billed weight as an overcharge or a discrepancy, or if it
objects to the fuel surcharge being computed on 100.0 kg.

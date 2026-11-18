---
type: llm
weight: 2
---

Judge only the text below, which audits an air freight invoice.

PASS if it accepts the fuel surcharge of 119.00 as correct and arrives at it as
140.0 kg x 0.85 per kg.
FAIL if it reports any charge as an overcharge or discrepancy, or if it computes the
fuel surcharge as a percentage of the 532.00 base freight.

---
type: llm
weight: 2
---

Judge only the text below, which audits an ocean freight invoice.

PASS if it accepts the BAF charge of 480.00 as correct and arrives at it by counting
2 x 40HC as 4 TEU at 120.00 per TEU.
FAIL if it reports the BAF as an overcharge or a discrepancy, if it computes BAF from a
percentage of ocean freight, or if it counts 2 x 40HC as 2 TEU.

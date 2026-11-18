---
type: llm
weight: 2
---

Judge only the text below, which audits a freight invoice.

PASS if it finds no billing errors and says the invoice can be paid as billed.
FAIL if it reports any CHARGE as an overcharge, as a discrepancy, or as needing
clarification before payment. Side observations that do not dispute a charge — on the
incoterm, on documents it did not receive, or on charges that were correctly absent —
do not count against it.

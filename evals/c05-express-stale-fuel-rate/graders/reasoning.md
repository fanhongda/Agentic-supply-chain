---
type: llm
weight: 2
---

Judge only the text below, which audits an express freight invoice.

PASS if it says the fuel surcharge used the wrong period's rate, that the rate in force
on the 2026-10-20 ship date was 22.0%, and that the correct amount is 88.00.
FAIL if it accepts the 24.5% rate as correct, if it selects the rate by the invoice date
of 2026-11-05, or if it reports the freight charge or the weight as wrong.

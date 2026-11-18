---
type: llm
weight: 2
---

Judge only the text below, which audits an express freight invoice.

PASS if it declines to confirm the EUR 470.00 against the USD 500.00 rate card and asks
for the exchange rate and the conversion date. Deriving the implied rate from 500 and 470
to show what would have to hold is fine and does not count against it.
FAIL if it states a variance or an over/under-charge amount for that line, if it concludes
the charge is correct, or if it substitutes a market exchange rate of its own choosing and
reasons from that.

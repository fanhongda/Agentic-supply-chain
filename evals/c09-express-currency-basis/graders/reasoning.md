---
type: llm
weight: 2
---

Judge only the text below, which audits an express freight invoice.

PASS if it says the EUR 470.00 charge cannot be checked against the USD 500.00 rate card
until the exchange rate and the conversion date are supplied, and asks for them.
FAIL if it applies an exchange rate of its own and then states a variance, or if it
concludes the charge is either correct or an overcharge.

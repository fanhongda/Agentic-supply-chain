---
type: llm
weight: 2
---

Judge only the text below, which audits an ocean freight invoice.

PASS if it treats the port congestion surcharge of 350.00 and the documentation amendment
fee of 75.00 as charges that need the carrier's justification because the quote does not
list them, and stops short of calling them definitively wrong.
FAIL if it states as settled fact that these charges are invalid or must be removed, or
if it accepts them as properly billed, or if it misses either one.

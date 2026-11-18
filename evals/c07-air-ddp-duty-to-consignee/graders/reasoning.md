---
type: llm
weight: 2
---

Judge only the text below, which audits an air freight invoice.

PASS if it objects to BOTH the destination handling charge of 180.00 AND the import duty
of 420.00, on the ground that the DDP term puts them on the seller rather than the
consignee being billed.
FAIL if it objects to only one of those two charges, if it accepts either as properly
billed, or if it also objects to the air freight of 980.00 or the fuel surcharge of
170.00.

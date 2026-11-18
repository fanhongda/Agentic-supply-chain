---
type: llm
weight: 2
---

Judge only the text below, which audits an ocean freight invoice.

PASS if it says the BAF charge is wrong because BAF is charged per TEU rather than as a
percentage of ocean freight, and gives 480.00 as the correct BAF.
FAIL if it treats the billed BAF of 720.00 as correct, or if it questions the BAF amount
without saying the charge basis itself is wrong.

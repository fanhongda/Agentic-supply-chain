---
name: logistics-billing-reconciliation
description: Audits a logistics freight invoice (express, sea LCL/FCL, or air) against the quote, rate card, and shipping documents, then reports line-item discrepancies with a pass/fail verdict.
---

# Logistics Billing Reconciliation

## When to Use This Skill

Use this skill whenever the user:

- shares a freight invoice or shipping bill (PDF or text) and wants it checked
- asks to verify, audit, or reconcile shipping charges — "check the invoice," "reconcile the bill,"
  "verify the freight charges"
- wants billed amounts compared against a quote or rate card
- needs a chargeable weight calculation, a fuel surcharge or BAF verification, or an incoterm
  compliance check

Carriers and modes covered: DHL Express, FedEx, Shun Feng (顺丰), sea freight forwarders (LCL and
FCL), and airlines. If the user uploads a carrier invoice from any of these, use this skill rather
than reconciling ad hoc — the charge bases (per kg, per TEU, per CBM, percentage) are easy to get
wrong and a wrong basis produces a confident wrong verdict.

Warehouse billing is a planned extension, not yet covered → `references/extension-points.md`.

## What This Skill Does

This skill walks through a structured audit of a logistics freight invoice, checking it against source documents (commercial invoice, packing list, quotes, rate cards) to surface billing errors, unauthorized surcharges, and incoterm violations. It produces a line-item reconciliation report with a clear pass/fail verdict.

**Current modules:**
| Module | Covers |
|--------|--------|
| Express | DHL Express, FedEx, Shun Feng — weight/dim, surcharges, duty/tax |
| Sea LCL / FCL | Quote verification, container params, accessorial charges |
| Air | Weight/dim, OHC/DHC, surcharges, incoterm compliance |

**Planned extension:** Warehouse billing → `references/extension-points.md`

---

## Step 1: Gather All Documents

Start by collecting what the user has. Use the `pdf` skill to read any PDFs (pdfplumber is preferred for structured extraction):

```python
import pdfplumber

def extract_pdf(path):
    with pdfplumber.open(path) as pdf:
        return [{"text": p.extract_text(), "tables": p.extract_tables()} for p in pdf.pages]
```

**Required documents:**
- Freight invoice (required — this is what we're auditing)
- Commercial invoice (required — for value, incoterm, and shipper/consignee)
- Packing list (required — for weight and dimensions per piece)
- Quote or rate card (required for rate verification)

**If the quote or rate card is missing**, say:

> "I need the original quote or rate card to verify the billed amounts. Please share the document, or paste the key rates as text. If you have a RAG system set up with rate data, I can query it instead."

<!-- RATE_LOOKUP: replace the prompt above with a structured query by (carrier, lane, service,
     effective_date, charge_type). Rate lookup is an exact query, not a vector search. -->

---

## Step 2: Extract Invoice Header Fields

From the freight invoice, extract these fields:

| Field | Description |
|-------|-------------|
| Invoice number | Unique billing reference |
| Account number | Carrier account number |
| Shipment / tracking number | AWB, BL, or booking reference |
| Service provider | Carrier name |
| Shipper | Origin party name |
| Consignee | Destination party name |
| Shipment origin | Origin port / city / country |
| Destination | Destination port / city / country |
| Inco-term | Trade term (EXW, FOB, CIF, DDP, DAP, etc.) |
| Invoice date | Billing date |
| Shipment date | Sailing / flight / pickup date — **required**: every surcharge lookup uses the rate effective on this date, not today's rate |
| Currency | Billing currency |

Present these to the user for confirmation before proceeding.

---

## Step 3: Identify Transport Mode → Route to Module

Apply these rules in order (first match wins):

1. **Service provider name** → DHL Express, FedEx, Shun Feng (顺丰) → **Express**
2. **Service type label on invoice** → "EXPRESS" → **Express** | "LCL" → **Sea LCL** | "FCL" → **Sea FCL**
3. **Document type clues** → VESSEL / OCEAN BILL OF LADING / HOUSE BILL OF LADING → **Sea** | AIRWAY BILL / MAWB / HAWB → **Air**

If the mode cannot be determined automatically, ask the user.

Once identified, read the corresponding reference file and run its checklist:

| Mode | Reference file |
|------|----------------|
| Express | `references/express-module.md` |
| Sea LCL or FCL | `references/sea-module.md` |
| Air | `references/air-module.md` |

Shared references used by every module:

| Reference | Covers |
|-----------|--------|
| `references/weight-rules.md` | Volumetric divisors, rounding increments, multi-piece aggregation, weight breaks, weight tolerance |
| `references/carrier-surcharge-urls.md` | Where to look up fuel/oil surcharge, BAF and CAF rates, and on which basis each is charged |

**Always resolve a surcharge rate as of the shipment date**, not the current published rate.

---

## Step 4: Produce the Reconciliation Report

After completing the module checklist, output a structured report using this exact template:

```
# Billing Reconciliation Report

**Invoice:** [number]  |  **Shipment:** [AWB/BL/ref]  |  **Carrier:** [name]
**Mode:** [Express / Sea LCL / Sea FCL / Air]  |  **Incoterm:** [term]
**Date:** [invoice date]  |  **Currency:** [currency]

## Overall Verdict
[ ✅ PASS / ❌ FAIL / ❓ REQUIRES CLARIFICATION ]
[One sentence summary of finding]

## Line-Item Results

| # | Charge | Basis & rate used | Billed | Expected | Variance | Status |
|---|--------|-------------------|--------|----------|----------|--------|
| 1 | Ocean freight | quote, 2 × 40HC | $1,200 | $1,200 | $0 | ✅ |
| 2 | BAF | $478/TEU × 4 TEU (notice eff. 2026-02-01) | $2,000 | $1,912 | +$88 | ❌ |
| 3 | Non-stackable surcharge | n/a — evidence pending | $90 | ? | ? | ❓ |

Status: ✅ matched  ❌ discrepancy  ❓ needs clarification

The **Basis & rate used** column is not optional. State the basis (per kg / per TEU / per CBM /
per revenue ton / percentage), the rate, and the rate's effective date for every computed line.
A figure without its basis cannot be disputed with a carrier.

## Discrepancies (❌)
[For each: what was billed, what was expected, the arithmetic that produced the
expected figure (inputs, basis, rate, effective date), and why it's wrong.]

## Items Needing Clarification (❓)
[For each: what information is needed, and who should provide it.]

## Incoterm Compliance Notes
[Flag any charges that conflict with the stated incoterm.]

## Next Steps
[Bulleted list of actions.]
```

---

## Modularity Notes (for future maintenance)

- Each transport mode is a self-contained reference file — update a module without touching this file.
- Surcharge sources and **charge bases** are centralized in `references/carrier-surcharge-urls.md` — add new carriers there.
- Weight arithmetic lives only in `references/weight-rules.md` — divisors, rounding increments, aggregation, and weight breaks are defined once and referenced by every module.
- Rate and surcharge lookup points are marked with `<!-- RATE_LOOKUP -->` in each module file.
- To add warehouse billing: create `references/warehouse-module.md` and add "Warehouse" to Step 3's routing table.

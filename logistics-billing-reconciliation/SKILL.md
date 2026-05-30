---
name: logistics-billing-reconciliation
description: Use this skill to reconcile, audit, or verify any logistics freight invoice or shipping bill. Trigger whenever the user shares a freight invoice (PDF or text), asks to check or verify shipping charges, wants to compare billed amounts against a quote or rate card, or needs to validate carrier charges for express, sea, or air shipments. Also trigger for chargeable weight calculations, fuel surcharge verification, incoterm compliance checks, or any request to "check the invoice," "reconcile the bill," or "verify the freight charges." If the user uploads a carrier invoice from DHL, FedEx, Shun Feng, a sea freight forwarder, or an airline, use this skill immediately — do not attempt to reconcile without it. Will be extended in the future to cover warehouse billing as part of an overall billing reconciliation suite.
---

# Logistics Billing Reconciliation

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

<!-- RAG_HOOK: Replace the above user prompt with a RAG query when a rate knowledge base is available. -->

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

For fuel/oil surcharge lookups in any module, refer to `references/carrier-surcharge-urls.md`.

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

| # | Charge | Billed | Expected | Variance | Status |
|---|--------|--------|----------|----------|--------|
| 1 | Ocean freight | $1,200 | $1,200 | $0 | ✅ |
| 2 | Fuel surcharge | $180 | $156 | +$24 | ❌ |
| 3 | Non-stackable surcharge | $90 | ? | ? | ❓ |

Status: ✅ matched  ❌ discrepancy  ❓ needs clarification

## Discrepancies (❌)
[For each: what was billed, what was expected, and why it's wrong.]

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
- Surcharge URLs are centralized in `references/carrier-surcharge-urls.md` — add new carriers there.
- All RAG integration points are marked with `<!-- RAG_HOOK -->` in each module file.
- To add warehouse billing: create `references/warehouse-module.md` and add "Warehouse" to Step 3's routing table.

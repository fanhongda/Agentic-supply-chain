# Sea Freight Module (LCL & FCL)

Applies to: invoices mentioning VESSEL, OCEAN BILL OF LADING, HOUSE BILL OF LADING, or service type LCL / FCL.

---

## Checklist

### 1. Quote / Rate Card Verification

If a dedicated RFQ or quote is provided:
- Compare every billed line item against the quoted amount.
- Any charge not present in the quote → ❓ (flag and ask for explanation)
- Any charge exceeding the quoted amount → ❌ (discrepancy)

If no quote is available:
> "Please share the original quote or rate card for this shipment. Without it I can't verify the billed rates."

<!-- RAG_HOOK: Replace the above prompt with a RAG query to retrieve the applicable sea freight rate for this lane (origin POL → destination POD), container type, and effective date. -->

---

### 2. Shipment Parameter Verification

Cross-check these fields between the invoice, quote/rate card, and bill of lading:

| Parameter | What to check |
|-----------|---------------|
| Container type | 20GP / 40GP / 40HC / LCL (CBM-based) |
| Container quantity | Must match BL and quote |
| Port of loading (POL) | Must match quote and BL |
| Port of discharge (POD) | Must match quote and BL |
| Incoterm | Must match commercial invoice |
| Movement type | Door-door / Port-port / Door-port / Port-door |
| Mode of transport | FCL / LCL / RoRo / Breakbulk |

Any mismatch → ❌

---

### 3. LCL-Specific Checks

- Billed volume (CBM) must match the packing list total volume. Variance > 0.1 CBM → ❌
- Freight rate = Billed CBM × rate per CBM (from quote)
- **Minimum CBM:** If actual CBM is below the carrier minimum (commonly 1 CBM), billed at minimum — verify the minimum is consistent with the quote.
- Weight-to-volume ratio: if actual weight exceeds 1,000 kg per CBM, some carriers bill by weight ton — confirm which basis was quoted.

---

### 4. FCL-Specific Checks

- All-in rate vs. component rate: confirm the billing structure matches the quote (some quotes are all-in; others list THC, documentation, BL fee separately).
- Verify each accessorial charge against the quote:
  - Terminal Handling Charge (THC) at origin and destination
  - Documentation fee / BL issuance fee
  - Seal fee, chassis fee (if applicable)
- Any accessorial not in the quote → ❓

---

### 5. Surcharge Verification

**BAF / CAF (Bunker Adjustment Factor / Currency Adjustment Factor):**
- Retrieve current carrier rate from `references/carrier-surcharge-urls.md`.
- Expected BAF = base ocean freight × BAF rate %.
- Variance > 2% → ❌

<!-- RAG_HOOK: Replace URL lookup with RAG query for current BAF/CAF by carrier, trade lane, and effective date. -->

**PSS / GRI / Other surcharges:**
- Check if each surcharge was explicitly included in the original quote.
- If billed but not in the quote → ❓ (requires carrier justification)

---

## Common Errors to Watch For

- Port pair mismatch between quote and invoice
- BAF charged at a different rate than what was locked in the quote
- Accessorial charges added post-quote without notification
- LCL CBM inflated beyond packing list volume

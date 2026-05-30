# Express Freight Module

Applies to: DHL Express, FedEx, Shun Feng (顺丰), and any invoice with service type "EXPRESS".

---

## Checklist

### 1. Weight & Dimension Verification

Extract from the **freight invoice**: actual weight (kg) and dimensions (L × W × H in cm) per piece.
Extract the same values from the **commercial invoice** and **packing list**.

Express carriers use carrier-specific volumetric divisors — do NOT use a single formula for all:

| Carrier | Volumetric divisor | Notes |
|---------|-------------------|-------|
| DHL Express | **5,000** cm³/kg | International express shipments |
| FedEx (International Priority / Economy) | **5,000** cm³/kg | International express shipments |
| Shun Feng (SF Express) | **6,000** cm³/kg | Most SF products; verify per service type |
| UPS (Worldwide Express) | **5,000** cm³/kg | |

```
Chargeable weight (kg) = L(cm) × W(cm) × H(cm) / [carrier divisor]
```

Billed weight should be: `MAX(actual weight, chargeable weight)` across all pieces.

Flag as ❌ if the billed chargeable weight differs from the calculated value by more than 0.5 kg.

---

### 2. Base Freight Rate

Compare the billed freight rate against the quote or rate card.

If no quote or rate card is available:
> "Please share the agreed rate card or original quote before I can verify the freight rate."

<!-- RAG_HOOK: Replace the above prompt with a RAG query to retrieve the applicable rate card for this carrier, origin, and destination. -->

---

### 3. Extra Charges

#### Non-Stackable Surcharge
If billed, ask:
> "Do you have a photo of the shipment that confirms it is non-stackable (e.g., machinery, irregular shape)?"

- If yes: mark as ❓ (pending evidence review)
- If no evidence: mark as ❓ (needs clarification before approval)

#### Overweight Surcharge
Carrier thresholds (per piece):
| Carrier | Threshold |
|---------|-----------|
| DHL Express | 70 kg |
| FedEx | 68 kg |
| Shun Feng | 50 kg |

If the surcharge is billed but no piece exceeds the threshold → ❌
If a piece exceeds the threshold but no surcharge is billed → ❓ (flag for review)

#### Fuel / Oil Surcharge
1. Retrieve the current rate from `references/carrier-surcharge-urls.md` for this carrier.
2. Expected surcharge = base freight charge × published rate %
3. Compare against billed surcharge amount.
4. Flag as ❌ if variance > 1%.

<!-- RAG_HOOK: Replace URL lookup with RAG query for current fuel surcharge rate by carrier and shipment date. -->

#### Duty and Tax
Check incoterm compliance:

| Incoterm | Expected behavior |
|----------|------------------|
| DDP | Seller pays all duties/taxes — consignee should NOT be billed separately |
| DAP | Buyer is responsible for import duties; billed to consignee is correct |
| EXW / FOB / CIF | Buyer responsible; billed to consignee is correct |

If duty or tax is billed to consignee under a DDP shipment → ❌ (incoterm violation)

---

## Common Errors to Watch For

- Carrier using wrong divisor (always confirm divisor with carrier tariff)
- Fuel surcharge applied at a rate from a prior month (carriers update monthly/weekly)
- Non-stackable charge added without physical justification
- Duty/tax billed under DDP shipments

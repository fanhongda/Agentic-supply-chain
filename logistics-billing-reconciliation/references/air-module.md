# Air Freight Module

Applies to: invoices mentioning AIRWAY BILL, MAWB, HAWB, or service type AIR.

Note: Standard air freight uses the IATA volumetric divisor of 6,000 cm³/kg. For express carriers (DHL Express, FedEx, UPS) using their express air products, use the express divisors in express-module.md instead.

---

## Checklist

### 1. Weight & Dimension Verification

Extract from the MAWB or HAWB: actual weight (kg) and dimensions (L × W × H in cm) per piece.
Extract same from the commercial invoice and packing list.

Standard air freight chargeable weight (IATA):
```
Chargeable weight (kg) = L(cm) × W(cm) × H(cm) / 6,000
```

Billed weight = `MAX(actual weight, chargeable weight)` across all pieces.

Flag as ❌ if billed chargeable weight differs from calculated value by more than 0.5 kg.

---

### 2. Base Freight Rate

Compare billed rate per kg against the quote or rate card.

If no quote or rate card:
> "Please share the agreed air freight rate or rate card before I can verify the freight charge."

<!-- RAG_HOOK: Replace the above prompt with a RAG query for the applicable air freight rate for this O&D pair, weight break, and shipment date. -->

---

### 3. Origin Handling Charges (OHC)

Verify the billed OHC against the quote.

Incoterm check:
| Incoterm | OHC responsibility |
|----------|-------------------|
| EXW | Seller does NOT pay OHC — buyer arranges pickup; OHC is buyer's cost |
| FOB / CIF | OHC typically on seller side — should not appear as a separate buyer charge |
| DDP | All handling included in seller's price — OHC should not be billed separately to consignee |
| DAP | OHC at origin is seller's; DHC at destination is buyer's |

If OHC appears on a consignee invoice under DDP → ❌ (incoterm violation)

---

### 4. Destination Handling Charges (DHC)

Verify billed DHC against the quote.

Incoterm check:
| Incoterm | DHC responsibility |
|----------|-------------------|
| DDP | Seller pays everything including DHC — should NOT appear as a separate charge to consignee |
| DAP | DHC is buyer's responsibility — charge to consignee is expected |
| EXW / FOB / CFR / CIF | DHC is buyer's responsibility — charge to consignee is expected |

If DHC is billed to consignee under a DDP shipment → ❌ (incoterm violation)

---

### 5. Extra Charges

#### Fuel Surcharge
1. Retrieve current rate from `references/carrier-surcharge-urls.md` for this carrier/airline.
2. Expected surcharge = base freight × published fuel surcharge rate %
3. Variance > 1% → ❌

<!-- RAG_HOOK: Replace URL lookup with RAG query for current air fuel surcharge by airline and shipment date. -->

#### Security Surcharge
- Should be a fixed rate per kg — verify it matches the quote.

#### Dangerous Goods (DG) Surcharge
- Only applicable if the shipment contains DG cargo.
- If billed: ask "Is there a Dangerous Goods Declaration for this shipment?"
- If no DG declaration: ❓ (needs clarification)

#### Remote Area Surcharge (RAS)
- Only applicable if origin or destination is a remote airport/city.
- If billed: confirm the location qualifies as remote per the carrier's zone list.
- If location is a major hub airport: ❌

---

## Common Errors to Watch For

- Chargeable weight rounded up beyond formula output
- DHC billed to consignee under DDP incoterm (most common incoterm violation in air billing)
- Fuel surcharge applied at wrong rate (airlines update monthly or bi-weekly)
- DG surcharge added to non-DG shipments

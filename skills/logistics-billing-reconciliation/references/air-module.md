# Air Freight Module

Applies to: invoices mentioning AIRWAY BILL, MAWB, HAWB, or service type AIR.

Standard air freight uses the IATA volumetric divisor of 6,000 cm³/kg. For express carriers
(DHL Express, FedEx, UPS) selling their express air products, use the express divisors instead →
`references/express-module.md`.

---

## Checklist

### 1. Weight & Dimension Verification

Follow `references/weight-rules.md` in full — divisor, 0.5 kg rounding increment, multi-piece
aggregation, weight breaks, and tolerance. Do not apply a separate tolerance here.

Air-specific inputs:
- Extract actual weight (kg) and dimensions (L × W × H in cm) **per piece** from the MAWB or HAWB.
- Extract the same from the commercial invoice and packing list.
- Divisor: **6,000** cm³/kg.
- Rounding increment: **0.5 kg, rounded up** (confirm against the carrier's tariff).

Reminder from the shared rules: a shipment billed at a **higher weight break** because the total
cost is lower is correct and favourable — it is not an overcharge.

---

### 2. Base Freight Rate

Compare the billed rate per kg against the quote or rate card, **at the applicable weight break**.

If no quote or rate card:
> "Please share the agreed air freight rate or rate card before I can verify the freight charge."

<!-- RATE_LOOKUP: query the air freight rate by (carrier, origin, destination, weight_break,
     effective_date). -->

---

### 3. Origin Handling Charges (OHC)

Verify the billed OHC against the quote.

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

| Incoterm | DHC responsibility |
|----------|-------------------|
| DDP | Seller pays everything including DHC — should NOT appear as a separate charge to consignee |
| DAP | DHC is buyer's responsibility — charge to consignee is expected |
| EXW / FOB / CFR / CIF | DHC is buyer's responsibility — charge to consignee is expected |

If DHC is billed to consignee under a DDP shipment → ❌ (incoterm violation)

---

### 5. Fuel Surcharge (FSC)

> ⚠️ **Air FSC is most commonly a rate per kg of chargeable weight, not a percentage of base
> freight.** Both bases exist and they are not interchangeable — establish the basis *before*
> computing an expected figure.

**Determine the basis first:**

| Basis | Formula | Notes |
|---|---|---|
| **Per kg** (most common) | `rate_per_kg × chargeable_weight` | Airlines publish FSC as e.g. USD 0.85/kg by region |
| Percentage | `base_freight × published_%` | Used by some carriers and most forwarder resale tariffs |

Two consequences of the per-kg basis:

1. **FSC scales with chargeable weight, not actual weight.** Use the billed weight derived in §1,
   including the rounding step. An FSC computed on actual weight when chargeable weight is higher
   understates it; computed on a weight higher than §1's figure, it is an overcharge → ❌.
2. **A weight-break discount does not reduce FSC.** The per-kg FSC applies to the billed weight
   regardless of which break the freight rate came from.

**Effective date matters:** airlines revise FSC **monthly or quarterly** against jet fuel indices.
Use the rate effective on the **shipment date**, not today's rate. Invoices commonly arrive after
the rate has moved — this is the highest-frequency source of false verdicts in both directions.

**Verification:**
1. Retrieve the carrier's FSC notice effective on the shipment date → `references/carrier-surcharge-urls.md`.
2. Read the **basis** from the notice (per kg or percentage), then compute per the table above.
3. Compare against the billed amount.

| Situation | Verdict |
|---|---|
| Matches within the currency rounding unit | ✅ |
| Billed higher | ❌ — show rate, basis, weight/base used, and the resulting figure |
| Billed lower | ❓ (carrier may re-bill) |
| Basis cannot be determined | ❓ — state both candidate figures; do not pick one |
| Quote was all-in / FSC-inclusive, yet FSC billed separately | ❌ (double recovery) |

<!-- RATE_LOOKUP: query air FSC by (carrier, region, effective_date) and return
     {basis: per_kg | percent, value}. -->

---

### 6. Other Extra Charges

#### Security Surcharge
Normally a **fixed rate per kg** of chargeable weight — verify both the rate and the basis against
the quote. Expect it to scale with the §1 billed weight, like FSC.

#### Dangerous Goods (DG) Surcharge
- Only applicable if the shipment contains DG cargo.
- If billed: ask "Is there a Dangerous Goods Declaration for this shipment?"
- If no DG declaration → ❓ (needs clarification)

#### Remote Area Surcharge (RAS)
- Applies only if origin or destination is on the carrier's published remote/extended-area list.
- If billed: confirm the location appears on that list for the shipment date.
- **Judge this against the carrier's list, not by whether the airport looks like a major hub** —
  a hub airport can still sit in an extended delivery area. Without the list → ❓, not ❌.

---

## Common Errors to Watch For

- **FSC computed as a percentage when the carrier publishes it per kg** (see §5), or vice versa
- FSC applied at a prior period's rate (airlines revise monthly or quarterly)
- FSC or security surcharge computed on actual weight instead of chargeable weight
- Chargeable weight rounded up beyond the billing increment (see `weight-rules.md` §2)
- A legitimate weight-break billing flagged as an overcharge (see `weight-rules.md` §4)
- DHC billed to consignee under DDP incoterm — the most common incoterm violation in air billing
- DG surcharge added to non-DG shipments
- RAS judged by intuition rather than the carrier's published area list

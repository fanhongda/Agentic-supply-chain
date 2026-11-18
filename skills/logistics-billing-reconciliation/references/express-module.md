# Express Freight Module

Applies to: DHL Express, FedEx, Shun Feng (顺丰), and any invoice with service type "EXPRESS".

---

## Checklist

### 1. Weight & Dimension Verification

Follow `references/weight-rules.md` in full — divisors, rounding increment, multi-piece aggregation,
weight breaks, and tolerance. Do not apply a separate tolerance here.

Express-specific inputs:
- Extract actual weight (kg) and dimensions (L × W × H in cm) **per piece** from the freight invoice.
- Extract the same from the commercial invoice and packing list.
- Divisor: **5,000** cm³/kg for DHL Express, FedEx International Priority/Economy, and UPS Worldwide
  Express; **6,000** for most Shun Feng products. Verify per service type.
- Rounding increment: **confirm against the carrier's tariff** — express increments vary by carrier
  and weight band. Do not assume the 0.5 kg air convention.

---

### 2. Base Freight Rate

Compare the billed freight rate against the quote or rate card, at the applicable weight break.

If no quote or rate card is available:
> "Please share the agreed rate card or original quote before I can verify the freight rate."

<!-- RATE_LOOKUP: query the rate card by (carrier, service, origin_zone, destination_zone,
     weight_break, effective_date). -->

---

### 3. Extra Charges

#### Fuel / Oil Surcharge
Express carriers publish FSC as a **percentage**, but the percentage does not always apply to base
freight alone — several carriers apply it to base freight **plus certain other surcharges**.

```
expected_FSC = applicable_base × published_rate_%
```

1. Retrieve the rate effective on the **shipment date** → `references/carrier-surcharge-urls.md`.
   DHL revises monthly, FedEx weekly — an invoice arriving after a revision is the most common
   source of false verdicts.
2. **Establish what the percentage applies to** from the carrier's tariff: base freight only, or
   base freight plus named surcharges. Using the wrong base is the same class of error as using
   the wrong rate.
3. Compute and compare.

| Situation | Verdict |
|---|---|
| Matches within the currency rounding unit | ✅ |
| Billed higher on a confirmed base and rate | ❌ |
| Billed lower | ❓ (carrier may re-bill) |
| Applicable base cannot be determined from the tariff | ❓ — state the figure under each candidate base |

<!-- RATE_LOOKUP: query express FSC by (carrier, region, effective_date) and return
     {rate_percent, applies_to: [freight, ...named surcharges]}. -->

#### Non-Stackable Surcharge
If billed, ask:
> "Do you have a photo of the shipment that confirms it is non-stackable (e.g., machinery, irregular shape)?"

- If yes: mark as ❓ (pending evidence review)
- If no evidence: mark as ❓ (needs clarification before approval)

#### Overweight Surcharge
Per-piece thresholds (confirm against the current tariff):

| Carrier | Threshold |
|---------|-----------|
| DHL Express | 70 kg |
| FedEx | 68 kg |
| Shun Feng | 50 kg |

- Surcharge billed but no piece exceeds the threshold → ❌
- A piece exceeds the threshold but no surcharge is billed → ❓ (flag for review)
- Judge against **actual** per-piece weight, not chargeable weight, unless the tariff says otherwise.

#### Duty and Tax
Check incoterm compliance:

| Incoterm | Expected behavior |
|----------|------------------|
| DDP | Seller pays all duties/taxes — consignee should NOT be billed separately |
| DAP | Buyer is responsible for import duties; billed to consignee is correct |
| EXW / FOB / CIF | Buyer responsible; billed to consignee is correct |

If duty or tax is billed to consignee under a DDP shipment → ❌ (incoterm violation)

Note: under DDP, carriers commonly bill a **duty-tax-paid / advancement fee to the shipper**. That
is a legitimate service fee and distinct from billing the duty itself to the consignee.

---

## Common Errors to Watch For

- Wrong divisor applied (always confirm the divisor against the carrier tariff)
- FSC applied at a prior period's rate (DHL monthly, FedEx weekly)
- **FSC percentage applied to the wrong base** (see §3)
- Billed weight rounded up beyond the tariff's increment (see `weight-rules.md` §2)
- A legitimate weight-break billing flagged as an overcharge (see `weight-rules.md` §4)
- Non-stackable charge added without physical justification
- Duty/tax billed to the consignee under DDP shipments

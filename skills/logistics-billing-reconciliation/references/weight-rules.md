# Chargeable Weight Rules (shared)

Single source of truth for how billable weight is derived. Express, air, and sea LCL modules
all reference this file — do not restate these rules or these tables in a module file.

> ⚠️ Every number below is a **default pending tariff confirmation**. Divisors, rounding
> increments, and aggregation conventions are contractual. Confirm each against the carrier's
> published tariff or the signed contract, and record what you confirmed in the Maintenance Log.

---

## The four steps, in order

Order matters. Applying the tolerance before the rounding step produces false positives.

```
1. Round each dimension        → per carrier convention (default: nearest whole cm)
2. Volumetric weight           = L(cm) × W(cm) × H(cm) / divisor
3. Chargeable weight (piece)   = MAX(actual weight, volumetric weight)
4. Billed weight (shipment)    = aggregate per §3, then round UP to the billing increment
```

---

## 1. Volumetric divisors

| Carrier / mode | Divisor (cm³/kg) | Notes |
|---|---|---|
| DHL Express | 5,000 | International express |
| FedEx (International Priority / Economy) | 5,000 | International express |
| UPS (Worldwide Express) | 5,000 | |
| Shun Feng (SF Express) | 6,000 | Varies by product — verify per service type |
| Standard air freight (IATA) | 6,000 | Use this for MAWB/HAWB air freight, **not** for express air products |
| Sea LCL | n/a | Billed on CBM or W/M — see `sea-module.md` |

---

## 2. Rounding increments

Carriers round the **final billed weight up** to a billing increment. This is legitimate, not an
overcharge, and it must be modelled before any comparison.

| Mode | Increment | Confidence |
|---|---|---|
| Standard air freight | 0.5 kg, rounded up | Commonly described as usual airline practice; some carriers use a different increment |
| Express | Verify per carrier tariff | Do **not** assume 0.5 kg; express increments vary by carrier and weight band |

```
billed_weight = ceil(aggregate_chargeable_weight / increment) × increment
```

**Example (air, 0.5 kg increment):** aggregate chargeable weight 72.1 kg → billed 72.5 kg.
Billing 72.5 kg here is **correct**. Billing 73.0 kg is one increment too high → ❌.

---

## 3. Multi-piece aggregation

Two conventions are in use and they give different answers. Getting this wrong can shift the
result by 10% or more, so confirm which one the contract uses.

| Convention | Formula | |
|---|---|---|
| **A — per-piece** | `Σ MAX(actual_i, volumetric_i)` | Compare piece by piece, then sum |
| **B — shipment total** | `MAX(Σ actual_i, Σ volume_i / divisor)` | Compare totals once |

Convention A yields a weight greater than or equal to convention B, never less.

If the contract is silent and the two conventions disagree on this shipment, report the
difference as ❓ with both figures — do not pick one and call the invoice wrong.

---

## 4. Weight breaks (air and express)

Rates drop at weight breaks. Common breaks: **45 / 100 / 250 or 300 / 500 / 1,000 kg**.
The 300 kg break is not universal, and in some countries the 45 kg break is replaced by 100 kg —
read the breaks off the rate card rather than assuming this ladder.

**The rule that prevents a whole class of false positives:**

A carrier may bill a shipment *at a higher break* when doing so costs less. This is legitimate
and standard practice.

> **Example.** 95 kg shipment. Rate is \$4.00/kg below 100 kg, \$3.50/kg at 100 kg and above.
> - Straight calculation: 95 × 4.00 = **\$380.00**
> - Billed at the 100 kg break: 100 × 3.50 = **\$350.00**
>
> The invoice shows 100 kg and \$350.00. This is **✅ correct and favourable to the payer**.
> Flagging "billed weight 100 kg exceeds chargeable weight 95 kg" here is a **false positive**.

So the expected freight charge is the cheapest legitimate option:

```
expected_freight = MIN(
    billed_weight × rate_at(billed_weight),          # charge at the shipment's own weight
    MIN over breaks b > billed_weight of ( b × rate_at(b) )   # or round up to a cheaper break
)
```

Both terms are required. Dropping the first one loses the ordinary case (95 kg × \$4.00 above);
dropping the second one reintroduces the false positive.

Compare the **total charge**, not the weight figure alone. Only flag a weight discrepancy when
the billed weight is higher *and* the resulting charge is higher than this minimum.

---

## 5. Tolerance

Once rounding (§2) and breaks (§4) are modelled explicitly, the expected weight is exact.

| Comparison | Tolerance | Verdict outside tolerance |
|---|---|---|
| Billed weight vs expected billed weight | **0.01 kg** (floating-point noise only) | Billed **higher** → ❌ overcharge. Billed **lower** → ❓ (carrier may re-bill) |
| Billed freight vs `expected_freight` (§4) | Currency rounding unit (e.g. \$0.01) | ❌ |

> **Do not use a 0.5 kg tolerance.** It was a proxy for unmodelled rounding and it fails in both
> directions: it hides a genuine 0.4 kg overcharge, and it fires on a legitimate rounding step.

---

## 6. Verification procedure

1. Extract actual weight and dimensions **per piece** from the packing list and the
   commercial invoice; extract billed weight from the freight invoice.
2. Cross-check the invoice's own stated weight against the shipping document (AWB / B/L).
   A mismatch here is a document problem, not a rate problem — report it separately.
3. Compute steps 1–4 using this file's tables plus the contract's divisor and increment.
4. Compare per §5. When reporting a discrepancy, show the arithmetic: dimensions used, divisor,
   volumetric weight, actual weight, aggregation convention, increment, and the resulting figure.

<!-- RATE_LOOKUP: divisor, rounding increment, aggregation convention, and the weight-break
     ladder are contract parameters. Query them as (carrier, service, contract_id, effective_date)
     rather than reading them from these default tables. -->

---

## Maintenance Log

| Date | Change |
|------|--------|
| 2026-11-18 | Initial version. Consolidates divisors from `express-module.md`, adds rounding increments, multi-piece aggregation, weight breaks, and replaces the 0.5 kg tolerance. |

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

<!-- RATE_LOOKUP: query the applicable sea freight rate by (carrier, POL, POD, container type,
     effective_date) instead of asking the user. -->

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
- **Billing basis — confirm which applies before computing anything:**

  | Basis | Formula | When used |
  |---|---|---|
  | Per CBM | `CBM × rate_per_cbm` | Light cargo |
  | **W/M (weight or measure)** | `MAX(CBM, weight_tonnes) × rate_per_wm` | Most LCL tariffs. Also called revenue ton or freight ton |

  A shipment of 2.0 CBM weighing 2,400 kg bills at **2.4 revenue tons** under W/M, not 2.0.
  Billing the higher of the two is correct — do not flag it as an overcharge.
- **Minimum:** if actual CBM is below the carrier minimum (commonly 1 CBM), billing at the minimum
  is correct — verify the minimum matches the quote.

---

### 4. FCL-Specific Checks

- All-in rate vs. component rate: confirm the billing structure matches the quote (some quotes are all-in; others list THC, documentation, BL fee separately).
- Verify each accessorial charge against the quote:
  - Terminal Handling Charge (THC) at origin and destination
  - Documentation fee / BL issuance fee
  - Seal fee, chassis fee (if applicable)
- Any accessorial not in the quote → ❓

---

### 5. BAF (Bunker Adjustment Factor)

> ⚠️ **BAF is a flat amount per container or per revenue ton — NOT a percentage of base freight.**
> Computing it as `base × %` produces a figure unrelated to what the carrier charges, in either
> direction. This is the single most common error in sea billing verification.

**Billing basis by mode:**

| Mode | Basis | Formula |
|---|---|---|
| **FCL** | USD per **TEU** | `rate_per_teu × TEU count` |
| FCL (some trades) | USD per **container**, by size | `rate_per_container × container count` |
| **LCL** | USD per **CBM** or per revenue ton | `rate_per_cbm × CBM` (or × revenue tons) |
| Rare | Percentage of base freight | Only if the contract explicitly says so — do not assume |

**TEU count:** 20GP = 1 TEU · 40GP = 2 TEU · 40HC = 2 TEU.

**Representative published figures** (illustrative only — always use the carrier's notice effective
on the shipment date):

| Trade | BAF | Effective |
|---|---|---|
| US West Coast | US$478 / TEU, or US$27.31 / revenue ton | 2026-02-01 |
| Australia – New Zealand | US$144 / TEU | 2026-02-01 |
| Inter-island | US$502 / TEU | 2026-02-01 |
| US – Caribbean (LCL) | US$0.55 / CBM | 2026 |

The spread between trades is roughly 3.5× per TEU, so **the trade lane must match** — a BAF looked
up on the wrong lane is not a smaller error than no lookup at all.

**Verification:**
1. Identify carrier, trade lane, and shipment date.
2. Retrieve the BAF notice effective **on the shipment date** → `references/carrier-surcharge-urls.md`.
3. `expected_BAF = published_rate × quantity` (TEU, container count, CBM, or revenue tons per the basis above).
4. Compare against the billed amount.

| Situation | Verdict |
|---|---|
| Matches the published rate × quantity | ✅ |
| Differs from it | ❌ — this is a published tariff figure, not an estimate; there is no tolerance band |
| Quote was **all-in** / BAF-inclusive, yet BAF is billed separately | ❌ (double recovery) |
| Quote locked a BAF figure, and the billed figure differs | ❌ — the locked figure governs, even if the published tariff moved |
| Basis cannot be determined from contract or notice | ❓ — state both candidate figures; do not guess |

<!-- RATE_LOOKUP: query BAF by (carrier, trade_lane, basis, effective_date) and return
     {basis: per_teu | per_container | per_cbm | per_revenue_ton | percent, value}. -->

---

### 6. CAF (Currency Adjustment Factor)

Unlike BAF, **CAF is normally expressed as a percentage** of base ocean freight, covering exchange-rate
movement between the tariff currency and the billing currency.

```
expected_CAF = base_ocean_freight × published_CAF_%
```

- Variance > 0.5% of the computed amount → ❌
- If the invoice currency equals the tariff currency, CAF generally should not apply → ❓
- Confirm whether the quote's base freight was CAF-inclusive before expecting a separate line.

---

### 7. Other Surcharges (PSS / GRI / congestion / peak season)

- Check whether each surcharge was explicitly included in the original quote.
- If billed but not in the quote → ❓ (requires carrier justification)
- GRI and PSS are announced per lane with an effective date: a surcharge whose effective date is
  **after** the shipment's sailing date should not apply → ❌

---

## Common Errors to Watch For

- **BAF computed as a percentage of base freight** (see §5) — wrong basis entirely
- BAF looked up on the wrong trade lane, or at today's rate instead of the sailing-date rate
- BAF billed separately on an all-in quote
- LCL billed per CBM when the tariff is W/M, or vice versa
- Port pair mismatch between quote and invoice
- Accessorial charges added post-quote without notification
- LCL CBM inflated beyond packing list volume
- A surcharge whose effective date postdates the sailing

# Carrier Surcharge Registry

Single source of truth for fuel / oil / bunker surcharge sources **and the basis each is charged on**.
Update this file when carriers change URLs, change basis, or when new carriers are onboarded.
Module files must NOT hardcode surcharge URLs or bases — always reference this file.

---

## The two rules that matter most

1. **Resolve the rate as of the shipment date, not today.** Invoices routinely arrive after the
   carrier has revised its rate. Most carrier pages publish only the current period, so a page fetch
   at audit time gives the wrong number. Until a snapshot table exists (roadmap Phase 3), record the
   rate you used **and the date you read it** in the report.
2. **Read the basis, not just the number.** The same surcharge name is charged on different bases
   across modes, and using the wrong basis produces a figure unrelated to the real charge:

   | Surcharge | Usual basis | Computed as |
   |---|---|---|
   | Express FSC | Percentage | `applicable_base × %` — confirm whether the base includes other surcharges |
   | Air FSC | **Per kg** of chargeable weight (percentage also exists) | `rate_per_kg × chargeable_weight` |
   | Air security surcharge | Per kg | `rate_per_kg × chargeable_weight` |
   | Sea **BAF** | **Per TEU / per container / per CBM / per revenue ton** — **never a percentage by default** | `rate × quantity` |
   | Sea **CAF** | Percentage of base ocean freight | `base_freight × %` |

---

## Express Carriers

| Carrier | Surcharge | Basis | URL | Revision frequency | Notes |
|---------|-----------|-------|-----|-----|-------|
| DHL Express | Fuel surcharge | Percentage | https://www.dhl.com/global-en/home/our-divisions/express/industry-insights/fuel-surcharge.html | Monthly | Rate table by country/zone |
| FedEx | Fuel surcharge | Percentage | https://www.fedex.com/en-us/shipping/fuel-surcharge.html | **Weekly** | Check the effective-date column carefully |
| Shun Feng (SF Express) | Fuel surcharge | Verify | https://www.sf-international.com | Ad hoc | Navigate to: Rates & Surcharges |

For express carriers, also confirm from the tariff **what the percentage applies to** — base freight
alone, or base freight plus named surcharges.

---

## Sea Carriers (BAF / CAF)

<!-- PLACEHOLDER: add confirmed sea carrier surcharge URLs below. -->
<!-- Format: | Carrier | Surcharge | Basis (per TEU / per container / per CBM / per revenue ton / %) | URL | Frequency | Notes | -->
<!-- To add: COSCO, MSC, Maersk, Evergreen, ONE -->

Until carrier pages are registered here, take BAF from the **carrier's own notice** for the trade
lane and effective period. Trade-lane coverage is not optional: published BAF spans roughly 3.5×
between lanes (e.g. US$144/TEU on Australia–New Zealand vs US$502/TEU inter-island, both effective
2026-02-01), so a figure from the wrong lane is not an approximation.

---

## Air Carriers (Fuel Surcharge)

<!-- PLACEHOLDER: add confirmed airline cargo fuel surcharge URLs below. -->
<!-- Format: | Airline | Surcharge | Basis (per kg / %) | URL | Frequency | Notes | -->
<!-- To add: Cathay Cargo, SIA Cargo, Emirates SkyCargo, Air China Cargo -->

Airlines revise FSC **monthly or quarterly** against jet fuel indices. Record the basis (per kg or
percentage) alongside the rate — see `references/air-module.md` §5.

---

## How to Use This File

1. Identify the carrier, the trade lane or region, and the **shipment date**.
2. Look up the source and the **basis** in the tables above.
3. Fetch the rate effective on the shipment date. If only the current period is published, say so in
   the report rather than silently using it.
4. Compute the expected surcharge on the stated basis.
5. Compare against the billed amount. If the basis cannot be established, report ❓ with the figure
   under each candidate basis — do not pick one.

<!-- RATE_LOOKUP:
When a rate store is available, replace the manual fetch with:
  surcharge = rates.lookup(carrier=..., charge_type="fuel"|"baf"|"caf",
                           lane=..., effective_date=shipment_date)
  -> {basis: percent | per_kg | per_teu | per_container | per_cbm | per_revenue_ton,
      value: ..., applies_to: [...], source_url: ..., fetched_at: ...}
This is an exact keyed query, not a vector search. The tables above are the seed data for
populating that store, and the snapshot schema needs (carrier, lane, basis, effective_from,
effective_to, value, source_url, fetched_at).
-->

---

## Maintenance Log

| Date | Change |
|------|--------|
| 2026-05-30 | Initial version — express carriers only |
| 2026-11-18 | Added **basis** to every entry and a basis summary table; corrected sea BAF from percentage to per-TEU/container/CBM/revenue-ton; separated CAF (percentage) from BAF; made shipment-date resolution explicit; renamed the RAG hook to `RATE_LOOKUP`. |

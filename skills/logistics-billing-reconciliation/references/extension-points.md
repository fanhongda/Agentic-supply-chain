# Extension Points

This file documents how to extend the skill to cover new billing types.

---

## Adding Warehouse Billing

When ready to add warehouse billing reconciliation:

1. Create `references/warehouse-module.md` with the warehouse billing checklist.
   Common items to cover:
   - Inbound handling fee (per pallet / per CBM / per line)
   - Storage fee (per day, per pallet position)
   - Outbound pick & pack fee
   - Special handling surcharges
   - Minimum monthly charges

2. In `SKILL.md` Step 3, add a new routing rule:
   ```
   "WAREHOUSE" / "STORAGE" / "HANDLING" in invoice → Warehouse
   ```
   And add a row to the module table:
   ```
   | Warehouse | `references/warehouse-module.md` |
   ```

3. Update the skill `description` in the SKILL.md frontmatter to mention warehouse billing.

4. Add warehouse-specific rate sources to `carrier-surcharge-urls.md` (or create a separate `warehouse-rate-registry.md`).

---

## Adding New Carriers (Surcharge URLs)

Add a row to the appropriate section of `references/carrier-surcharge-urls.md`.
No changes to any module file are needed.

---

## Rate & Surcharge Lookup Integration

Lookup points are marked with `<!-- RATE_LOOKUP -->` in:
- `SKILL.md` (rate card prompt)
- `references/express-module.md` (rate card, fuel surcharge)
- `references/sea-module.md` (rate card, BAF)
- `references/air-module.md` (rate card, fuel surcharge)
- `references/weight-rules.md` (divisor, increment, aggregation, weight breaks)
- `references/carrier-surcharge-urls.md` (surcharge lookup)

Two different mechanisms, and the distinction matters:

| Need | Mechanism | Why |
|---|---|---|
| Rates, surcharges, divisors, weight breaks | **Exact keyed query** (Dataverse table or MCP tool) | Parameters are precise: carrier, lane, service, container type, effective-date range. A vector search over a rate card returns plausible neighbours, which is the worst possible failure mode for a number you are about to dispute |
| Contract clause wording, carrier tariff prose | Vector search (RAG) | Free text, no key to query on |

When integrating:
1. Replace each `<!-- RATE_LOOKUP -->` comment's preceding user prompt with the keyed query.
2. Query parameters always include: carrier, lane (origin→destination), charge_type, effective_date.
3. The response must carry the **basis**, not just a value — see `carrier-surcharge-urls.md`.
4. If the lookup returns no result, fall back to the user prompt — don't silently skip the check.

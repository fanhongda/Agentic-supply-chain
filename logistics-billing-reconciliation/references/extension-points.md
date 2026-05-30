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

## RAG Integration

All RAG integration points are marked with `<!-- RAG_HOOK -->` in:
- `SKILL.md` (rate card prompt)
- `references/express-module.md` (rate card, fuel surcharge)
- `references/sea-module.md` (rate card, BAF)
- `references/air-module.md` (rate card, fuel surcharge)
- `references/carrier-surcharge-urls.md` (surcharge lookup)

When integrating RAG:
1. Replace each `<!-- RAG_HOOK -->` comment's preceding user prompt with a RAG query.
2. The query parameters are always: carrier, lane (origin→destination), effective_date, charge_type.
3. If RAG returns no result, fall back to the user prompt — don't silently skip the check.

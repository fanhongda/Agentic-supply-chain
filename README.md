# Agentic Supply Chain

A collection of agentic tools and Claude skills for supply chain operations — built for practitioners who want AI to do the routine work so they can focus on decisions that matter.

## Skills

### [`logistics-billing-reconciliation`](./logistics-billing-reconciliation/)

A structured Claude skill for auditing freight invoices against source documents. Catches billing errors, unauthorized surcharges, and incoterm violations before you pay.

**Covers:**
- **Express** — DHL Express, FedEx, Shun Feng: chargeable weight (carrier-specific divisors), fuel surcharge verification, duty/tax incoterm checks
- **Sea LCL / FCL** — Quote vs. invoice comparison, container parameters, BAF/CAF verification
- **Air** — Weight/dimension checks, origin & destination handling charges, DDP/DAP incoterm compliance

**Designed to grow:**
- Plug in new carrier surcharge URLs without touching core logic
- RAG hooks marked throughout — swap user prompts for rate database queries when ready
- Extension point for warehouse billing as the next module

---

## Roadmap

- [ ] Warehouse billing reconciliation module
- [ ] Sea carrier surcharge URL registry (COSCO, MSC, Maersk, Evergreen)
- [ ] Air carrier fuel surcharge registry (Cathay Cargo, SIA Cargo, Emirates SkyCargo)
- [ ] RAG integration for live rate card lookups
- [ ] Combined billing dashboard (freight + warehouse)

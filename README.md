# Agentic Supply Chain

A collection of agentic tools and Claude skills for supply chain operations — built for practitioners who want AI to do the routine work so they can focus on decisions that matter.

## Design & research

- [`design.md`](./design.md) — architecture, and how each asset maps onto the target platform
- [`research/2026-11-landscape.md`](./research/2026-11-landscape.md) — open-source landscape, data sources, testing approaches

**Target platform:** this work ships on Microsoft Copilot Studio (the sanctioned agent platform here);
Claude Code is the development and evaluation environment. Keep contributions portable — see `design.md` §4–5
for what carries over and what does not. In short: domain knowledge stays in `SKILL.md` + `references/`,
deterministic calculation belongs in the MCP server, and nothing in the production path may rely on
shell access or the local filesystem.

---

## Skills

### [`logistics-billing-reconciliation`](./logistics-billing-reconciliation/)

A structured Claude skill for auditing freight invoices against source documents. Catches billing errors, unauthorized surcharges, and incoterm violations before you pay.

**Covers:**
- **Express** — DHL Express, FedEx, Shun Feng: chargeable weight (carrier-specific divisors), fuel surcharge verification, duty/tax incoterm checks
- **Sea LCL / FCL** — Quote vs. invoice comparison, container parameters, BAF/CAF verification
- **Air** — Weight/dimension checks, origin & destination handling charges, DDP/DAP incoterm compliance

**Designed to grow:**
- Plug in new carrier surcharge URLs without touching core logic
- `RATE_LOOKUP` hooks marked throughout — swap user prompts for keyed rate-store queries when ready
- Extension point for warehouse billing as the next module

---

## Roadmap

- [ ] Warehouse billing reconciliation module
- [ ] Sea carrier surcharge URL registry (COSCO, MSC, Maersk, Evergreen)
- [ ] Air carrier fuel surcharge registry (Cathay Cargo, SIA Cargo, Emirates SkyCargo)
- [ ] Rate store for live rate card and surcharge lookups (keyed query, not vector search)
- [ ] Combined billing dashboard (freight + warehouse)

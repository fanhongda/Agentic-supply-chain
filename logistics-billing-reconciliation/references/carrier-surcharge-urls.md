# Carrier Surcharge URL Registry

This file is the single source of truth for fuel/oil surcharge rate pages.
Update this file when carriers change URLs or when new carriers are onboarded.
Module files must NOT hardcode surcharge URLs — always reference this file.

---

## Express Carriers

| Carrier | Surcharge type | URL | Update frequency | Notes |
|---------|---------------|-----|-----------------|-------|
| DHL Express | Fuel surcharge | https://www.dhl.com/global-en/home/our-divisions/express/industry-insights/fuel-surcharge.html | Monthly | Rate table shows % by country/zone |
| FedEx | Fuel surcharge | https://www.fedex.com/en-us/shipping/fuel-surcharge.html | Weekly | Check the effective date column carefully |
| Shun Feng (SF Express) | Fuel surcharge | https://www.sf-international.com | Ad hoc | Navigate to: Rates & Surcharges section |

---

## Sea Carriers (BAF / CAF)

<!-- PLACEHOLDER: Add confirmed sea carrier surcharge URLs below -->
<!-- Format: | Carrier | BAF/CAF | URL | Frequency | Notes | -->
<!-- Examples to add: COSCO, MSC, Maersk, Evergreen, ONE -->

---

## Air Carriers (Fuel Surcharge)

<!-- PLACEHOLDER: Add confirmed airline cargo fuel surcharge URLs below -->
<!-- Format: | Airline | Fuel surcharge | URL | Frequency | Notes | -->
<!-- Examples to add: Cathay Cargo, SIA Cargo, Emirates SkyCargo, Air China Cargo -->

---

## How to Use This File in Reconciliation

1. Identify the carrier from the invoice.
2. Look up the URL in this table.
3. Fetch the page and find the rate effective for the shipment date.
4. Use that rate to calculate the expected surcharge.
5. Compare against the billed surcharge.

<!-- RAG_HOOK:
When a rate database (RAG) is available, replace the manual URL fetch with:
  rate = rag.query(carrier=carrier_name, surcharge_type="fuel", effective_date=shipment_date)
The URL table above serves as the seed data for populating and maintaining that RAG knowledge base.
-->

---

## Maintenance Log

| Date | Change |
|------|--------|
| 2026-05-30 | Initial version — express carriers only |

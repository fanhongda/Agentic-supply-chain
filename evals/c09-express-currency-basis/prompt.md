---
max_turns: 20
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep, Skill]
tags: [adversarial]
---

Can you check this freight invoice for me? I want to know whether we should pay it as billed. Everything I have is below.

## Freight invoice (the document under audit)

```
DHL EXPRESS — FREIGHT INVOICE
Invoice number: DE-2026-118977        Invoice date: 2026-11-13
Account number: 950114227
Shipment / waybill: 7712338002        Ship date: 2026-11-06
Service: EXPRESS WORLDWIDE
Shipper: Ningbo Hartman Tools Co. Ltd, Ningbo CN
Consignee: Kessler Werkzeug GmbH, Dusseldorf DE
Origin: Ningbo, CN                    Destination: Dusseldorf, DE
Incoterm: FOB Ningbo                  Currency: EUR
Pieces: 6   Actual weight: 72.0 kg    Billed weight: 72.0 kg
----------------------------------------------------
Express freight, 72.0 kg, zone 5           470.00
----------------------------------------------------
TOTAL DUE                              EUR 470.00
(No exchange rate or conversion date stated on this invoice.)
```

## Packing list

```
PACKING LIST
Cartons 1-6: 45 x 35 x 25 cm each, gross 12.0 kg each
Total: 6 cartons, 72.0 kg
```

## Commercial invoice

```
COMMERCIAL INVOICE
Seller: Ningbo Hartman Tools Co. Ltd      Date: 2026-11-05
Buyer: Kessler Werkzeug GmbH
Incoterm: FOB Ningbo
Goods: Impact driver sets, 190 units      Value: USD 14,440.00
Gross weight: 72.0 kg
```

## Rate card

```
DHL EXPRESS RATE CARD — contract CN-2026-0042, valid 2026-07-01 to 2026-12-31
Currency: USD. Volumetric divisor: 5000 cm3/kg
Zone 5 (DE), EXPRESS WORLDWIDE: 72.0 kg = USD 500.00
Contract is silent on billing currency and on the exchange rate basis.
```

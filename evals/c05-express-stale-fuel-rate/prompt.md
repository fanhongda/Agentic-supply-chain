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
Invoice number: DE-2026-117290        Invoice date: 2026-11-05
Account number: 950114227
Shipment / waybill: 7709338471        Ship date: 2026-10-20
Service: EXPRESS WORLDWIDE
Shipper: Ningbo Hartman Tools Co. Ltd, Ningbo CN
Consignee: Kessler Werkzeug GmbH, Dusseldorf DE
Origin: Ningbo, CN                    Destination: Dusseldorf, DE
Incoterm: FOB Ningbo                  Currency: USD
Pieces: 5   Actual weight: 57.0 kg    Billed weight: 57.0 kg
Dimensions: 5 pieces @ 45 x 35 x 25 cm
----------------------------------------------------
Express freight, 57.0 kg, zone 5           400.00
Fuel surcharge @ 24.5%                      98.00
----------------------------------------------------
TOTAL DUE                                  498.00
```

## Packing list

```
PACKING LIST
Cartons 1-5: 45 x 35 x 25 cm each, gross 11.4 kg each
Total: 5 cartons, 57.0 kg
```

## Commercial invoice

```
COMMERCIAL INVOICE
Seller: Ningbo Hartman Tools Co. Ltd      Date: 2026-10-19
Buyer: Kessler Werkzeug GmbH
Incoterm: FOB Ningbo
Goods: Impact driver sets, 150 units      Value: USD 11,400.00
Gross weight: 57.0 kg
```

## Rate card

```
DHL EXPRESS RATE CARD — contract CN-2026-0042, valid 2026-07-01 to 2026-12-31
Volumetric divisor: 5000 cm3/kg
Zone 5 (DE), EXPRESS WORLDWIDE: 57.0 kg = USD 400.00
```

## Carrier surcharge notice

```
DHL EXPRESS FUEL SURCHARGE
Effective 2026-10-01 to 2026-10-31: 22.0%
Effective 2026-11-01 to 2026-11-30: 24.5%
Applies to: express freight charge.
```

---
max_turns: 20
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep, Skill]
tags: [clean]
---

Can you check this freight invoice for me? I want to know whether we should pay it as billed. Everything I have is below.

## Freight invoice (the document under audit)

```
DHL EXPRESS — FREIGHT INVOICE
Invoice number: DE-2026-118842        Invoice date: 2026-11-12
Account number: 950114227
Shipment / waybill: 7712094558        Ship date: 2026-11-05
Service: EXPRESS WORLDWIDE
Bill to: Kessler Werkzeug GmbH (CONSIGNEE)
Shipper: Ningbo Hartman Tools Co. Ltd, Ningbo CN
Consignee: Kessler Werkzeug GmbH, Dusseldorf DE
Origin: Ningbo, CN     Destination: Dusseldorf, DE
Pieces: 2    Actual weight: 16.0 kg    Billed weight: 16.0 kg
Dimensions: 2 pieces @ 40 x 30 x 20 cm
Currency: USD
----------------------------------------------------
Express freight, 16.0 kg, zone 5          112.00
Fuel surcharge @ 24.5%                     27.44
----------------------------------------------------
TOTAL DUE                                 139.44
```

## Commercial invoice

```
COMMERCIAL INVOICE
Seller: Ningbo Hartman Tools Co. Ltd      Date: 2026-11-04
Buyer: Kessler Werkzeug GmbH
Incoterm: FOB Ningbo
Goods: 400 x hardened drill bit set       Value: USD 6,240.00
Gross weight: 16.0 kg    Packages: 2 cartons
```

## Packing list

```
PACKING LIST
Carton 1: 40 x 30 x 20 cm, gross 8.0 kg, 200 sets
Carton 2: 40 x 30 x 20 cm, gross 8.0 kg, 200 sets
Total: 2 cartons, 16.0 kg
```

## Rate card

```
DHL EXPRESS RATE CARD — contract CN-2026-0042, valid 2026-07-01 to 2026-12-31
Volumetric divisor: 5000 cm3/kg
Zone 5 (DE), EXPRESS WORLDWIDE, USD:
  14.0 kg  98.00  |  15.0 kg 105.00  |  16.0 kg 112.00  |  17.0 kg 119.00
```

## Carrier surcharge notice

```
DHL EXPRESS FUEL SURCHARGE
Effective 2026-10-01 to 2026-10-31: 22.0%
Effective 2026-11-01 to 2026-11-30: 24.5%
Applies to: express freight charge.
```

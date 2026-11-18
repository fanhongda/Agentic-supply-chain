---
max_turns: 20
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep, Skill]
tags: [negative-control]
---

Can you check this freight invoice for me? I want to know whether we should pay it as billed. Everything I have is below.

## Freight invoice (the document under audit)

```
SKYBRIDGE AIR CARGO — FREIGHT INVOICE
Invoice number: SB-26-77410           Invoice date: 2026-11-15
Master air waybill: 160-55188123
Flight date: 2026-11-08
Service: AIR FREIGHT
Shipper: Hangzhou Vertex Electronics Co. Ltd
Consignee: Adler Systemtechnik GmbH, Frankfurt DE
Origin: Shanghai PVG, CN              Destination: Frankfurt FRA, DE
Incoterm: FCA Shanghai                Currency: USD
Pieces: 1   Actual weight: 95.0 kg    Chargeable weight: 95.0 kg
Dimensions: 1 piece @ 100 x 70 x 60 cm
Billed weight: 100.0 kg (charged at the +100 kg weight break)
----------------------------------------------------
Air freight, 100.0 kg @ 3.50/kg            350.00
Fuel surcharge, 100.0 kg @ 0.85/kg          85.00
----------------------------------------------------
TOTAL DUE                                  435.00
```

## Packing list

```
PACKING LIST
Crate 1: 100 x 70 x 60 cm, gross 95.0 kg
Total: 1 crate, 95.0 kg
```

## Commercial invoice

```
COMMERCIAL INVOICE
Seller: Hangzhou Vertex Electronics Co. Ltd   Date: 2026-11-07
Buyer: Adler Systemtechnik GmbH
Incoterm: FCA Shanghai
Goods: Power conversion modules, 210 units    Value: USD 31,400.00
Gross weight: 95.0 kg
```

## Rate card

```
SKYBRIDGE AIR RATE CARD — PVG to FRA, valid 2026-10-01 to 2026-12-31
Volumetric divisor: 6000 cm3/kg. Chargeable weight rounded up to 0.5 kg.
Weight breaks, USD per kg:
  +45 kg   4.20  |  +100 kg  3.50  |  +300 kg  3.10
Charging at a higher weight break is permitted where the resulting total is lower.
```

## Carrier surcharge notice

```
SKYBRIDGE FUEL SURCHARGE — Asia outbound
Effective 2026-11-01: USD 0.85 per kg
Basis: per kg of billed weight.
```

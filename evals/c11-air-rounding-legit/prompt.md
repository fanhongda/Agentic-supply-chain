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
Invoice number: SB-26-77455           Invoice date: 2026-11-15
Master air waybill: 160-55190447
Flight date: 2026-11-08
Service: AIR FREIGHT
Shipper: Wuxi Caldera Instruments Co. Ltd
Consignee: Adler Systemtechnik GmbH, Frankfurt DE
Origin: Shanghai PVG, CN              Destination: Frankfurt FRA, DE
Incoterm: FCA Shanghai                Currency: USD
Pieces: 1   Actual weight: 50.0 kg
Dimensions: 1 piece @ 95 x 60 x 55 cm
Volumetric weight: 95 x 60 x 55 / 6000 = 52.25 kg
Billed weight: 52.5 kg (rounded up to the 0.5 kg increment)
----------------------------------------------------
Air freight, 52.5 kg @ 4.00/kg             210.00
Fuel surcharge, 52.5 kg @ 0.80/kg           42.00
----------------------------------------------------
TOTAL DUE                                  252.00
```

## Packing list

```
PACKING LIST
Crate 1: 95 x 60 x 55 cm, gross 50.0 kg
Total: 1 crate, 50.0 kg
```

## Commercial invoice

```
COMMERCIAL INVOICE
Seller: Wuxi Caldera Instruments Co. Ltd      Date: 2026-11-07
Buyer: Adler Systemtechnik GmbH
Incoterm: FCA Shanghai
Goods: Calibration benches, 4 units           Value: USD 22,800.00
Gross weight: 50.0 kg
```

## Rate card

```
SKYBRIDGE AIR RATE CARD — PVG to FRA, valid 2026-10-01 to 2026-12-31
Volumetric divisor: 6000 cm3/kg. Chargeable weight rounded UP to 0.5 kg.
Weight breaks, USD per kg:
  +45 kg   4.00  |  +100 kg  3.50  |  +300 kg  3.10
```

## Carrier surcharge notice

```
SKYBRIDGE FUEL SURCHARGE — Asia outbound
Effective 2026-11-01: USD 0.80 per kg
Basis: per kg of chargeable weight.
```

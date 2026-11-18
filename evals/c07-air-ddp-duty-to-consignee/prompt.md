---
max_turns: 20
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep, Skill]
tags: [adversarial]
---

Can you check this freight invoice for me? I want to know whether we should pay it as billed. Everything I have is below.

## Freight invoice (the document under audit)

```
SKYBRIDGE AIR CARGO — FREIGHT INVOICE
Invoice number: SB-26-77588           Invoice date: 2026-11-16
Master air waybill: 160-55194880
Flight date: 2026-11-09
Service: AIR FREIGHT
Bill to: Crestline Medical Devices Inc (CONSIGNEE)
Shipper: Shenzhen Anhe Biotech Co. Ltd
Consignee: Crestline Medical Devices Inc, Los Angeles CA US
Origin: Shanghai PVG, CN              Destination: Los Angeles LAX, US
Incoterm: DDP Los Angeles             Currency: USD
Pieces: 2   Actual weight: 200.0 kg   Chargeable weight: 200.0 kg
----------------------------------------------------
Air freight, 200.0 kg @ 4.90/kg            980.00
Fuel surcharge, 200.0 kg @ 0.85/kg         170.00
Destination handling charge                180.00
Import duty and tax advanced               420.00
----------------------------------------------------
TOTAL DUE                                1,750.00
```

## Commercial invoice

```
COMMERCIAL INVOICE
Seller: Shenzhen Anhe Biotech Co. Ltd        Date: 2026-11-08
Buyer: Crestline Medical Devices Inc
Incoterm: DDP Los Angeles
Goods: Infusion pump assemblies, 80 units    Value: USD 96,000.00
Gross weight: 200.0 kg
```

## Quote

```
QUOTE SB-Q-26-2240, valid 2026-11-01 to 2026-11-30
Lane: PVG -> LAX, air freight, DDP
Air freight: USD 4.90 per kg of chargeable weight
Fuel surcharge: as per carrier notice on flight date
All destination charges, duties and taxes included in the seller's DDP price.
```

## Carrier surcharge notice

```
SKYBRIDGE FUEL SURCHARGE — Asia outbound
Effective 2026-11-01: USD 0.85 per kg
Basis: per kg of chargeable weight.
```

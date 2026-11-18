---
max_turns: 20
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep, Skill]
tags: [adversarial]
---

Can you check this freight invoice for me? I want to know whether we should pay it as billed. Everything I have is below.

## Freight invoice (the document under audit)

```
SF EXPRESS (SHUN FENG) — FREIGHT INVOICE
Invoice number: SF-26-330915          Invoice date: 2026-11-10
Account number: SF7741208
Shipment number: SF4471229088         Ship date: 2026-11-03
Service: EXPRESS
Shipper: Dongguan Ruicheng Hardware Co. Ltd
Consignee: Pacific Fastening Supply Inc, Long Beach CA US
Origin: Dongguan, CN                  Destination: Long Beach CA, US
Incoterm: FOB Shenzhen                Currency: USD
Pieces: 1   Actual weight: 15.0 kg    Billed weight: 24.0 kg
Dimensions: 1 piece @ 60 x 50 x 40 cm
Volumetric calculation shown on invoice: 60 x 50 x 40 / 5000 = 24.0 kg
----------------------------------------------------
Express freight, 24.0 kg @ 2.80/kg          67.20
Fuel surcharge @ 16.0%                      10.75
----------------------------------------------------
TOTAL DUE                                   77.95
```

## Packing list

```
PACKING LIST
Carton 1: 60 x 50 x 40 cm, gross 15.0 kg
Total: 1 carton, 15.0 kg
```

## Commercial invoice

```
COMMERCIAL INVOICE
Seller: Dongguan Ruicheng Hardware Co. Ltd    Date: 2026-11-02
Buyer: Pacific Fastening Supply Inc
Incoterm: FOB Shenzhen
Goods: Stainless socket screws, 60 boxes      Value: USD 3,180.00
Gross weight: 15.0 kg
```

## Rate card

```
SF EXPRESS RATE CARD — contract CN-2026-SF-11, valid 2026-01-01 to 2026-12-31
Volumetric divisor: 6000 cm3/kg
CN -> US West, EXPRESS: USD 2.80 per kg of chargeable weight
Fuel surcharge: 16.0% of express freight charge.
```

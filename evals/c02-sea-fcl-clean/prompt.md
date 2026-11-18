---
max_turns: 20
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep, Skill]
tags: [clean]
---

Can you check this freight invoice for me? I want to know whether we should pay it as billed. Everything I have is below.

## Freight invoice (the document under audit)

```
MERIDIAN LOGISTICS — OCEAN FREIGHT INVOICE
Invoice number: ML-26-004417          Invoice date: 2026-03-02
Ocean bill of lading: MEDUSH4471220
Vessel / voyage: MSC AMALFI / 606W    Sailing date: 2026-02-10
Service: FCL
Shipper: Suzhou Linwell Precision Co. Ltd
Consignee: Brouwer Industrial BV, Rotterdam NL
Port of loading: Shanghai, CN         Port of discharge: Rotterdam, NL
Containers: 2 x 40HC                  Movement: Port-port
Incoterm: FOB Shanghai                Currency: USD
----------------------------------------------------
Ocean freight, 2 x 40HC @ 2,400.00       4,800.00
BAF, 4 TEU @ 120.00/TEU                    480.00
Terminal handling charge, destination      240.00
Documentation fee                           50.00
----------------------------------------------------
TOTAL DUE                                5,570.00
```

## Quote

```
QUOTE ML-Q-26-0881, valid for sailings 2026-02-01 to 2026-02-28
Lane: Shanghai (CNSHA) -> Rotterdam (NLRTM), FCL, port-port
Ocean freight: USD 2,400.00 per 40HC
Terminal handling charge, destination: USD 120.00 per container
Documentation fee: USD 50.00 per bill of lading
BAF: as per carrier notice in force on the sailing date — NOT included above
```

## Commercial invoice

```
COMMERCIAL INVOICE
Seller: Suzhou Linwell Precision Co. Ltd     Date: 2026-02-06
Buyer: Brouwer Industrial BV
Incoterm: FOB Shanghai
Goods: CNC spindle housings, 1,240 units     Value: USD 184,600.00
```

## Carrier surcharge notice

```
CARRIER BAF NOTICE
Trade: Asia -> North Europe
Effective 2026-02-01: USD 120.00 per TEU
Effective 2026-03-01: USD 134.00 per TEU
Basis: per TEU. 20ft = 1 TEU, 40ft and 40HC = 2 TEU.
```

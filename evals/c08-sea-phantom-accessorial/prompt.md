---
max_turns: 20
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep, Skill]
tags: [adversarial]
---

Can you check this freight invoice for me? I want to know whether we should pay it as billed. Everything I have is below.

## Freight invoice (the document under audit)

```
MERIDIAN LOGISTICS — OCEAN FREIGHT INVOICE
Invoice number: ML-26-004731          Invoice date: 2026-03-09
Ocean bill of lading: MEDUSH4490277
Vessel / voyage: MSC TRIESTE / 611W   Sailing date: 2026-02-24
Service: FCL
Shipper: Qingdao Northline Ceramics Co. Ltd
Consignee: Verhoeven Tiles BV, Rotterdam NL
Port of loading: Qingdao, CN          Port of discharge: Rotterdam, NL
Containers: 1 x 40GP                  Movement: Port-port
Incoterm: FOB Qingdao                 Currency: USD
----------------------------------------------------
Ocean freight, 1 x 40GP                  1,500.00
Terminal handling charge, destination      180.00
Documentation fee                           45.00
Port congestion surcharge                  350.00
Documentation amendment fee                 75.00
----------------------------------------------------
TOTAL DUE                                2,150.00
```

## Quote

```
QUOTE ML-Q-26-0934, valid for sailings 2026-02-01 to 2026-02-28
Lane: Qingdao (CNTAO) -> Rotterdam (NLRTM), FCL, port-port
Ocean freight: USD 1,500.00 per 40GP
Terminal handling charge, destination: USD 180.00 per container
Documentation fee: USD 45.00 per bill of lading
No other charges apply unless separately notified in writing before sailing.
```

## Commercial invoice

```
COMMERCIAL INVOICE
Seller: Qingdao Northline Ceramics Co. Ltd   Date: 2026-02-20
Buyer: Verhoeven Tiles BV
Incoterm: FOB Qingdao
Goods: Porcelain floor tiles, 18 pallets     Value: USD 27,400.00
```

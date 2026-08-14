---
title: "Couchdb Performance on a MacPro"
description: "See the differences in on the Mac Pro"
date: 2010-09-28
tags:
- amazon 
- cloud
- couchcb 
- erlang 
- python 
- performance 
- benchmark 
- read


draft: false
---

# Couchdb Performance on MacPro

## Inserting

Using:
```
Couchdb 0.11.0
2x3 QUAD-Core Intel Xeon
16 GB 667Mhz DDR2
OS X 10.6.4
```

## Inserting


| NUM | BLOCK | time. | Bytes. | Mb/s. | records/s. |
|----:|------:|------:|-------:|------:|----------:|
| 1	| 1	| 0.0030	| 1	| 0.000	| 330
| 10	| 1	| 0.0251	| 100	| 0.004	| 398
| 1000	| 1	| 3.2415	| 1000000	| 0.308	| 308
| 10000	| 1	| 34.6263	| 100000000	| 2.888	| 289
| 1000	| 10	| 3.4122	| 10610000	| 3.109	| 2931
| 100	| 100	| 1.5112	| 10601000	| 7.015	| 6617
| 10	| 1000	| 1.9464	| 10600100	| 5.446	| 5138
| 2	| 5000	| 2.3308	| 10600020	| 4.548	| 4290
| 1	| 10000	| 2.0068	| 10600010	| 5.282	| 4983
| 10	| 10000	| 15.7176	| 106000100	| 6.744	| 6362

## Average Top:

| | | | | | | | | | |
|-------:|---------:|------:|---------:|---:|---:|-----:|---:|---:| ---:|
| 33423  | beam.smp | 48.9  | 05:42.89 | 13 | 0  | 62  | 151-  | 39M-   | 264K  |
| 33421  | CouchDBX     | 12.9      | 00:52.85 | 6/1   | 3    | 124- | 322   | 77M-   | 29M   |


---
title: "My First Super Computer"
description: "Speeding up Monte Carlo using GPU"
date: 2010-10-01
tags:
- benchmark
- GPU
- cuda 
- GeForce
- Monte Carlo
- risk 
- NVIDIA 
- performance


draft: false
---

# My First Super Computer 

Using:
```
Macbook Air
1.86 Ghz Intel Core 2 Duo
2 GB 1067 Mhz DDR3
GeForce 9400M

Total amount of global memory: 265945088 bytes
Number of multiprocessors: 2
Number of cores: 16
```

## Monte Carlo

### Options : 256


| Simulation paths | CPU Time (ms.) | CPU options/sec. | GPU Time (ms.) | GPU options/sec. |
|----:|------:|------:|-------:|------:|
| 262144	| 8000	| 32.6	| 246	| 1041	| 
| 131072	| 4000	| 64	| 128	| 2005	| 
| 65536	| 2000	| 128	| 	63.12	| 4056	| 


I was thinking of building a big GPU box does anyone have any ideas ?


I'm thinking of getting:
EVGA Classified SR-2 (Super Record 2) 270-WS-W555-A1 LGA 1366 Intel 5520 SATA 6Gb/s USB 3.0 HPTX Intel Motherboard.
Adding 48 Gig and then plugging in 4 GeForce GTX 480 ??

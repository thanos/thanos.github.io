---
title: "My Second Super Computer"
description: "Speeding up Monte Carlo using AWS GPU Instances"
date: 2010-12-01
tags:
- benchmark
- GPU
- cuda 
- GeForce
- Monte Carlo
- risk 
- NVIDIA 
- performance
- AWS

draft: false
---

# My Second Super Computer 


Using:
```
Cluster GPU Quadruple Extra Large 22 GB 
memory: 22 GB
EC2 Compute Units: 33.5 , 
GPU: 2 x NVIDIA Tesla “Fermi” M2050 GPUs, 
1690 GB of local instance storage, 64-bit platform, 10 Gigabit Ethernet

cores each: 448 
os: CENTOS 64bit
```

## Monte Carlo on One Telsa Device

### Options : 256


| Simulation paths | CPU Time (ms.) | CPU options/sec. | GPU Time (ms.) | GPU options/sec. |
|----:|------:|------:|-------:|------:|
| 262144	| 6000	| 42	| 3.586	| 71388	| 


## Monte Carlo on Two Telsa Devices

### Options : 256 split across two Tesla boards

| Simulation paths | CPU Time (ms.) | CPU options/sec. | GPU Time (ms.) | GPU options/sec. |
|----:|------:|------:|-------:|------:|
| 262144	| 6000	| 42	| 3.405	| 151999	| 


## TOTAL Cost: $0.04
including building the environment and sample code from scratch.

```
CUDA Device Query (Runtime API) version (CUDART static linking)

There are 2 devices supporting CUDA

Device 0: "Tesla M2050"
  CUDA Driver Version:                           3.20
  CUDA Runtime Version:                          3.10
  CUDA Capability Major/Minor version number:    2.0
  Total amount of global memory:                 2817982464 bytes
  Multiprocessors x Cores/MP = Cores:            14 (MP) x 32 (Cores/MP) = 448 (Cores)
  Total amount of constant memory:               65536 bytes
  Total amount of shared memory per block:       49152 bytes
  Total number of registers available per block: 32768
  Warp size:                                     32
  Maximum number of threads per block:           1024
  Maximum sizes of each dimension of a block:    1024 x 1024 x 64
  Maximum sizes of each dimension of a grid:     65535 x 65535 x 1
  Maximum memory pitch:                          2147483647 bytes
  Texture alignment:                             512 bytes
  Clock rate:                                    1.15 GHz
  Concurrent copy and execution:                 Yes
  Run time limit on kernels:                     No
  Integrated:                                    No
  Support host page-locked memory mapping:       Yes
  Compute mode:                                  Default (multiple host threads can use this device simultaneously)
  Concurrent kernel execution:                   Yes
  Device has ECC support enabled:                Yes

Device 1: "Tesla M2050"
  CUDA Driver Version:                           3.20
  CUDA Runtime Version:                          3.10
  CUDA Capability Major/Minor version number:    2.0
  Total amount of global memory:                 2817982464 bytes
  Multiprocessors x Cores/MP = Cores:            14 (MP) x 32 (Cores/MP) = 448 (Cores)
  Total amount of constant memory:               65536 bytes
  Total amount of shared memory per block:       49152 bytes
  Total number of registers available per block: 32768
  Warp size:                                     32
  Maximum number of threads per block:           1024
  Maximum sizes of each dimension of a block:    1024 x 1024 x 64
  Maximum sizes of each dimension of a grid:     65535 x 65535 x 1
  Maximum memory pitch:                          2147483647 bytes
  Texture alignment:                             512 bytes
  Clock rate:                                    1.15 GHz
  Concurrent copy and execution:                 Yes
  Run time limit on kernels:                     No
  Integrated:                                    No
  Support host page-locked memory mapping:       Yes
  Compute mode:                                  Default (multiple host threads can use this device simultaneously)
  Concurrent kernel execution:                   Yes
  Device has ECC support enabled:                Yes

deviceQuery, CUDA Driver = CUDART, CUDA Driver Version = 3.20, CUDA Runtime Version = 3.10, NumDevs = 2, Device = Tesla M2050, Device = Tesla M2050
```
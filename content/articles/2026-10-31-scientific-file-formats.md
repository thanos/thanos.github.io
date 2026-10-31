---
title: "Scientific File Formats"
description: "The formats science actually consolidates around — ASDF, Zarr, CRAM, Parquet, Arrow — and a comparative review of libraries in Java, C#, C, Zig, Rust, Python, Elixir, Fortran, and Ruby."
date: 2026-10-31
tags:
  - scientific computing
  - file formats
  - HDF5
  - Zarr
  - Parquet
  - Arrow
  - genomics
  - geospatial
  - Elixir
  - Rust
  - Zig
draft: false
authors:
  - Thanos Vassilakis
---

There are hundreds of niche scientific extensions. The interesting story is not the long tail — it is how cutting-edge work has consolidated around a smaller set of next-generation, high-performance, multi-dimensional open formats: cloud-optimized chunks, columnar analytics, and parallel I/O that survive petabyte pipelines.

This is a map of those formats by domain, then a comparative look at what you can actually call from Java, C#, C, Zig, Rust, Python, Elixir, Fortran, and Ruby. The library picture changes faster than the formats; treat the tables as a field guide, not a warranty.

## Astronomy and space sciences

Modern telescopes — JWST, Roman, and the ground-based survey machines behind them — produce multi-band datasets that need structured metadata as much as raw pixels.

- **ASDF** (Advanced Scientific Data Format) — modern successor to FITS for many new missions. YAML/JSON-schema metadata plus efficient binary array blocks; designed for validation and extension tags rather than 80-byte card images.
- **FITS 4** — still the interchange lingua franca. Version 4 adds better checksums, compression for large images, and tighter world-coordinate / time handling under the IAU standard.
- **HDF5** (`.h5` / `.hdf5`) — filesystem-in-a-file for simulations and instruments that outgrew flat FITS tables. Self-describing groups, datasets, attributes, chunking, and filters.

## Genomics, bioinformatics, and health

Next-generation sequencing and single-cell multi-omics need streaming reads and brutal compression over millions of base pairs.

- **CRAM** — reference-based relative encoding; stores differences against a known genome instead of full alignments. Usually much smaller than BAM for the same content.
- **BAM** — binary Sequence Alignment/Map; the workhorse machine-readable form of SAM.
- **VCF / BCF** — variants: SNPs, indels, and structural calls with a schema that tools actually agree on.
- **h5ad** (AnnData) — de facto standard for single-cell transcriptomics in the Python/scanpy world: sparse expression matrix plus observation/variable annotations in one HDF5-shaped container.
- **Loom** — HDF5 layout for high-dimensional single-cell matrices with row/column attributes.

## Geospatial, climate, and environment

Earth observation and climate models are four-dimensional (lat, lon, height/depth, time) and often live on object storage rather than a single POSIX file.

- **Zarr** — chunked, compressed N-dimensional arrays as many objects (local dir, S3, GCS). Parallel web I/O without opening one giant file handle.
- **Cloud Optimized GeoTIFF (COG)** — tiled TIFF with overviews so HTTP range requests fetch only the pixels you need.
- **NetCDF-4** — climate/ocean/weather currency; NetCDF-4 rides on HDF5 under the hood while keeping the classic scientific data model (dimensions, variables, attributes).
- **GeoPackage** — SQLite container for vectors, tiles, and rasters; open and non-proprietary.
- **LAZ** — compressed LiDAR point clouds; the dense 3D counterpart to LAS.

## Big data, physics simulations, and HPC

When pipelines hit petabyte scale, science borrows storage ideas from analytics engines.

- **Apache Parquet** — columnar on disk; predicate pushdown and compression that make analytical scans cheap.
- **Apache Arrow / Feather** — columnar *in memory* (and IPC on disk); zero-copy sharing across languages when everyone speaks Arrow.
- **Avro** — row-oriented binary with an embedded JSON schema; common in streaming pipelines where schemas evolve.
- **F3** (Future-proof File Format) — CMU Database Group experiment: columnar layout that can embed WebAssembly decoders so the file carries its own reader. Early, but points at where “format plus codec” is heading.

## Format comparison

| Format | Core domain | Architecture | Why it wins |
| --- | --- | --- | --- |
| ASDF | Astronomy | YAML metadata + binary blocks | Schema-validated mission interchange |
| FITS 4 | Astronomy | Header/data units | Universal legacy + improved compression |
| HDF5 | Cross-domain | Hierarchical groups/datasets | Self-describing HPC arrays |
| Zarr | Geospatial / climate | Chunked objects | Cloud-native parallel I/O |
| NetCDF-4 | Climate / ocean | Dimensions + variables on HDF5 | Shared scientific data model |
| CRAM | Genomics | Reference-relative alignments | Storage collapse vs BAM |
| BAM / VCF | Genomics | Indexed binary / text+binary | Toolchain gravity |
| Parquet | Analytics / HPC adjacent | Columnar disk | Scan and skip performance |
| Arrow | Cross-language | Columnar memory / IPC | Zero-copy interchange |
| F3 | Research / HPC | Columnar + embedded Wasm | Self-describing decoders |
| COG | Geospatial | Tiled TIFF + overviews | HTTP partial reads |
| GeoPackage | Geospatial | SQLite container | Portable vectors + rasters |
| LAZ | LiDAR | Compressed point cloud | Dense 3D at manageable size |

## Comparative library review

Formats only matter if your language can open them. Below: primary libraries for the formats that show up most often in scientific stacks. Blank or “thin” cells mean no serious first-class library I would ship on — use FFI to C, or convert upstream.

Maturity key: **reference** = de facto / official; **strong** = production-grade community; **usable** = works with caveats; **thin** = early or niche; **gap** = use another language or bind C.

### Coverage matrix (high level)

| Format | Python | C | Rust | Java | C# | Elixir | Fortran | Ruby | Zig |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| HDF5 | reference | reference | strong / evolving | strong | strong | thin (via FFI / convert) | reference | thin | gap |
| NetCDF | reference | reference | usable | strong | usable | thin | reference | thin | gap |
| Zarr | reference | via NetCDF-C / C++ | strong | strong | thin | strong | thin | gap | gap |
| Parquet | reference | via Arrow C++ | reference | reference | strong | strong (via Arrow) | gap | usable | usable → strong |
| Arrow | reference | reference (C / C++) | reference | reference | strong | strong | thin | strong (C GLib) | usable |
| FITS | reference | reference (CFITSIO) | usable | strong | usable | gap | via CFITSIO | thin | gap |
| ASDF | reference | strong | thin | read-oriented | gap | gap | gap | gap | gap |
| BAM/CRAM/VCF | reference | reference (HTSlib) | strong | reference (htsjdk) | thin | gap | gap | usable (aging FFI) | gap |

### Python — still the scientific front door

If a format matters, Python usually has the nicest API and the most examples.

| Format | Libraries | Notes |
| --- | --- | --- |
| HDF5 | `h5py`, PyTables | Bindings to the HDF Group C library |
| NetCDF / Zarr | `netCDF4`, `xarray`, `zarr` | xarray sits on both NetCDF and Zarr |
| FITS / ASDF | Astropy `io.fits`, `asdf`, `asdf-astropy` | ASDF reference implementation is Python |
| Genomics | `pysam` (HTSlib), `anndata`, `scanpy` | BAM/CRAM/VCF + h5ad |
| Parquet / Arrow | `pyarrow`, `fastparquet`, Polars/pandas | Arrow is the shared memory story |
| Geospatial | `rasterio`, `rioxarray`, GDAL bindings | COG/GeoTIFF via GDAL |

**Verdict:** richest ecosystem. Production science pipelines still default here for interactive work and for defining interchange.

### C — where the durable cores live

| Format | Libraries | Notes |
| --- | --- | --- |
| HDF5 | HDF5 C API | Official; parallel HDF5 for MPI |
| NetCDF | NetCDF-C | Can expose Zarr stores in recent lines |
| FITS | CFITSIO | Reference FITS; Fortran-callable |
| Genomics | HTSlib | SAM/BAM/CRAM/VCF/BCF, BGZF, tabix |
| ASDF | asdf-c | Spec-track C implementation |
| Arrow | Arrow C / nanoarrow | C Data Interface for zero-copy handoff |

**Verdict:** if you need longevity, MPI, or something every other language wraps, start in C (or accept that you will).

### Fortran — still first-class for arrays on disk

| Format | Libraries | Notes |
| --- | --- | --- |
| HDF5 | HDF5 Fortran bindings | Official, with the C library |
| NetCDF | netCDF-Fortran | Climate/ocean model staple |
| FITS | CFITSIO Fortran API | Same core as C |
| Parquet / Zarr / Arrow | — | Generally gap; call C or preprocess |

**Verdict:** excellent for HDF5/NetCDF/FITS in HPC models. Columnar cloud formats are not where Fortran spends its energy.

### Java — enterprise science and genomics tooling

| Format | Libraries | Notes |
| --- | --- | --- |
| HDF5 | Official Java bindings; JHDF (pure Java read); sis-jhdf5 | Mix of JNI and pure Java |
| NetCDF / scientific | **netCDF-Java** | Reads NetCDF, HDF5, GRIB, BUFR |
| Zarr | `zarr-java`, JZarr, n5-zarr, netCDF-Java paths | Multiple implementations |
| FITS | `nom.tam.fits` | Mature FITS 4 support |
| ASDF | Java reader (read-focused) | Weaker than Python/C |
| Genomics | **htsjdk** | BAM/CRAM/VCF with HTSlib-class gravity |
| Parquet / Arrow | parquet-java, Arrow Java | First-class analytics stack |

**Verdict:** strongest non-Python home for genomics (htsjdk) and a serious NetCDF/HDF5/Zarr story for Earth science JVMs.

### C# / .NET — managed readers catching up

| Format | Libraries | Notes |
| --- | --- | --- |
| HDF5 | **PureHDF** (managed), HDF.PInvoke / HDF5-CSharp | PureHDF avoids native deps |
| Parquet | **Parquet.Net**, ParquetSharp | Parquet.Net is pure managed |
| Arrow | Apache Arrow C# | Official implementation |
| FITS | CSharpFITS, FitsLib, JPFITS | Usable, not astronomy’s center |
| NetCDF / Zarr | thinner / bindings | Often via C APIs or conversion |
| Genomics | thin | Prefer JVM or Python pipelines |

**Verdict:** Parquet and HDF5 are genuinely good on modern .NET. Domain formats (Zarr, CRAM, ASDF) lag.

### Rust — safe reimplementations and good FFI

| Format | Libraries | Notes |
| --- | --- | --- |
| Arrow / Parquet | `arrow`, `parquet` (arrow-rs) | Official Rust implementations |
| Zarr | `zarrs` | Listed on zarr.dev; v2/v3 |
| HDF5 / NetCDF / FITS | `hdf5` crates (often FFI), emerging pure ports (e.g. consus line) | Ecosystem split: bind C vs rewrite |
| Genomics | **noodles** | Pure Rust BAM/CRAM/VCF/FASTA/… |
| ASDF | limited | Prefer Python for authorship |

**Verdict:** Arrow/Parquet/Zarr/noodles are the places Rust already feels production-native. Hierarchical science formats are improving but still dual-track (FFI vs pure).

### Elixir — BEAM-native where it counts

| Format | Libraries | Notes |
| --- | --- | --- |
| Zarr | **ExZarr** | Pure Elixir v2/v3; CI-tested against zarr-python |
| Arrow / Parquet | **ex_arrow** | IPC, Flight, ADBC, Parquet, Dataset |
| HDF5 / NetCDF / FITS / HTS | — | Convert or NIF to C; not BEAM-native yet |

**Verdict:** for cloud-chunked arrays and columnar interchange on the BEAM, the story is real. For FITS/HDF5/CRAM, plan a boundary service or NIF.

### Ruby — bindings and BioRuby, not format leadership

| Format | Libraries | Notes |
| --- | --- | --- |
| Arrow / Parquet | red-arrow, red-parquet (GObject / Arrow C++) | Solid if you accept native deps |
| Genomics | bio-samtools (FFI to samtools/HTSlib) | Works; maintenance is uneven |
| FITS / HDF5 / Zarr | thin / archived gems | Prefer conversion pipelines |

**Verdict:** fine as a consumer via Arrow or bio-samtools. Not where new scientific format work happens.

### Zig — early but pointed at columnar I/O

| Format | Libraries | Notes |
| --- | --- | --- |
| Parquet | **zig-parquet** | Pure Zig read/write, codecs, Arrow C Data ABI |
| Arrow | zarrow, arrow-zig | Native layouts + IPC; maturing |
| HDF5 / NetCDF / Zarr / FITS / HTS | gap | Bind C or stay in another language |

**Verdict:** Zig’s interesting scientific niche today is *columnar* (Parquet/Arrow), not the classic HPC hierarchy formats. Expect rapid change.

## How to choose

1. **Interchange with astronomers** — FITS everywhere; ASDF when the mission already standardized on it (Python/C first).
2. **Climate / Earth arrays on object stores** — Zarr (+ xarray); NetCDF-4 when the model community demands it.
3. **Genomics alignments and variants** — HTSlib / pysam / htsjdk / noodles; CRAM for cold storage.
4. **Analytics over tables** — Parquet on disk, Arrow in process; language choice matters less once Arrow is the glue.
5. **BEAM services** — ExZarr and ex_arrow for Zarr/Arrow/Parquet; do not pretend HDF5 or CRAM are first-class on Elixir yet.
6. **Systems languages without a science runtime** — C cores, or Rust when you want memory safety and are willing to live with crate churn.

## Closing

Scientific formats stopped being “whatever the instrument vendor shipped” and became a small set of architectural bets: hierarchical files (HDF5/NetCDF), cloud chunks (Zarr/COG), reference compression (CRAM), and columnar analytics (Parquet/Arrow). Language support follows those bets unevenly. Python and C still define the center; Java owns much of genomics tooling; Rust and Elixir are credible where formats are specs rather than 30-year C APIs; Zig is entering through Parquet/Arrow; Fortran remains indispensable for the models that never left NetCDF/HDF5; Ruby and C# are selective rather than universal.

If you are picking a stack for a new pipeline, pick the **format** for the access pattern first, then the language that already has a boring library for it. Inventing a fifteenth niche extension is almost never the hard part anymore — reading it in ten years, from three languages, on object storage, is.

## References

1. [CMU Database Group — Future File Formats](https://db.cs.cmu.edu/projects/future-file-formats/)
2. [ASDF overview](https://www.asdf-format.org/en/latest/overview.html)
3. [ASDF implementations](https://www.asdf-format.org/en/latest/implementations/index.html)
4. [NASA — FITS Standard Version 4](https://science.data.nasa.gov/features-events/fits-standard-version-4-released)
5. [NASA — FITS I/O libraries](https://science.data.nasa.gov/fits/libraries)
6. [Zarr implementations](https://zarr.dev/implementations/)
7. [Apache Arrow implementation status](https://arrow.apache.org/docs/status.html)
8. [HTSlib](https://github.com/samtools/htslib)
9. [noodles (Rust)](https://docs.rs/noodles/latest/noodles/)
10. [ExZarr](https://hex.pm/packages/ex_zarr)
11. [ex_arrow](https://hex.pm/packages/ex_arrow)
12. [PureHDF](https://apollo3zehn.github.io/PureHDF/)
13. [Parquet.Net](https://github.com/aloneguid/parquet-dotnet/)
14. [zig-parquet](https://github.com/akeating/zig-parquet)
15. [F3 — Future-proof File Format](https://github.com/future-file-format/f3)

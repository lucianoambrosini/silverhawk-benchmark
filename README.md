<div align="center">
<img src="https://ambrosinus.altervista.org/blog/wp-content/uploads/2026/04/SilverHawk_Banner_dev.jpg" width="70%" height="70%">
</div>

# SilverHawk Benchmark — Replication Package

[![DOI](https://img.shields.io/badge/DOI-10.5281%2Fzenodo.20630810-1682D4)](https://doi.org/10.5281/zenodo.20630810)
[![Paper](https://img.shields.io/badge/paper-Automation%20in%20Construction%20(submitted)-informational)](https://www.sciencedirect.com/journal/automation-in-construction)
[![Data license: CC BY 4.0](https://img.shields.io/badge/data-CC%20BY%204.0-blue.svg)](https://creativecommons.org/licenses/by/4.0/)
[![Code license: MIT](https://img.shields.io/badge/code-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Release](https://img.shields.io/github/v/release/lucianoambrosini/silverhawk-benchmark?include_prereleases&label=release)](https://github.com/lucianoambrosini/silverhawk-benchmark/releases)

**Companion to:** *"SilverHawk: Metaheuristic Optimization for Architectural Design Under Severe Computational Budget Constraints"* (Ambrosini, submitted to *Automation in Construction*, 2026).

**Maintainer:** Luciano Ambrosini (LA Architecture & Computational Design Consulting, Naples, Italy) — luciano.ambrosini@outlook.com · ORCID 0000-0003-1529-2694

**Version:** 1.0-rc (populated for AiC submission). The package will be tagged **v1.0** at journal acceptance and **v1.1** at SilverHawk public release on food4Rhino.

---

## Purpose

This replication package supports independent verification of the entire benchmark campaign reported in the paper (~28,685 independent optimization runs, ~140 million function evaluations across 25 problems and six dimensionalities D ∈ {10, 15, 20, 22, 30, 85}). Reproducibility is offered at three levels, two available now for peer review and one at the SilverHawk public release (see *Two-phase release strategy* below).

Reviewers and readers can use it to:

1. **Verify** (available now) the numerical claims of the paper — rankings, hypervolume values, convergence profiles, NFL evidence — directly against the released per-run raw outputs.
2. **Regenerate** (available now) every figure and statistic from the published per-figure source data and the analysis scripts.
3. **Re-execute** (at plugin release) any headless benchmark layer byte-for-byte, using the pre-built Falconry console under the canonical seed schedule, and **extend** the canvas layers with the SH_BenchmarkADO Grasshopper component — both shipped in Phase 2 with the SilverHawk food4Rhino release.


---

## Hardware envelope

All benchmark campaigns reported in the paper were executed on a single workstation:

| Component | Specification                                                                                             |
| --------- | --------------------------------------------------------------------------------------------------------- |
| CPU       | Intel Core i7-4770K (Haswell, 4 cores / 8 threads, 3.5 GHz base / 3.9 GHz turbo, 22 nm, released Q2 2013) |
| RAM       | 32 GB DDR3                                                                                                |
| Storage   | Kingston SSD (447 GB) primary + Toshiba HDD (932 GB) secondary                                            |
| GPU       | NVIDIA GeForce GTX 1650 (4 GB) — not used by the benchmarks (CPU-bound)                                   |
| OS        | Windows 64-bit                                                                                            |
| Software  | Rhinoceros 8 SR15, Grasshopper, Karamba3D 3.2, SilverHawk plugin (versions per layer)                     |

This is a **2013-vintage CPU**, two generations older than the Skylake/Kaby Lake workstations typical of the most-cited prior ADO benchmarks (Cichocka et al. 2017; Wortmann 2017). A timing pilot on a contemporary ASUS ROG Flow 2025 laptop indicated a 60–70% wall-clock reduction on representative SilverHawk loads, suggesting that the wall-clock numbers in the paper conservatively understate performance on current hardware.

Wall-clock measurements in the paper are valid only within this hardware envelope. Replication on different hardware will reproduce identical *numerical results* (algorithm rankings, hypervolume values, fitness statistics) under the documented seed schedule (`seed = 5000 + r × 137`), but wall-clock absolute timings will differ.

---

## Two-phase release strategy

This package is released in two phases to align with the publication timeline of the SilverHawk plugin itself.

### Phase 1 — AiC peer-review (v0.1 → v1.0 at acceptance)

Available immediately for reviewers and at journal acceptance:

- **Benchmark data** — per-run CSV outputs for all five layers (`data/`).
- **Surrogate models** — Ambrosini GBR + ANN v2 serialized in scikit-learn JSON format (`surrogate/`).
- **Analysis scripts** — surrogate training and learning-curve scripts (`scripts/`).
- **Source data for figures** — per-figure underlying tables (`figures_source_data/`).

### Phase 2 — Post-publication, SilverHawk food4Rhino release (v1.1)

Added after the AiC paper appears online and the SilverHawk plugin is published on food4Rhino:

- **Falconry C# console source** — standalone benchmark console (`falconry/`).
- **SH_BenchmarkADO Grasshopper component** — the GBR + ANN v2 inferencer embedded as a GH black-box (`grasshopper_assets/SH_BenchmarkADO.gh`).
- **Synthetic benchmark Grasshopper files** — Sphere, Rastrigin, Rosenbrock, Schwefel, Step (D = 10 native components) (`grasshopper_assets/SH_Benchmark_synthetic.gh`).
- **Pugnale K3D Kakamigahara Grasshopper file** — the canonical D = 85 structural benchmark with Karamba3D pipeline (`grasshopper_assets/SH_BenchmarkK3D_Kakamigahara.gh`), redistributed with attribution per the original Pugnale & Sassone (2007) licence terms.

The two-phase release ensures the peer-review process has full access to the numerical evidence even before the plugin itself enters public distribution.

---

## Folder structure

```
replication_package/
├── README.md                            (this file — master)
├── MANIFEST.md                          (file-by-file inventory + SHA256)
├── data/
│   ├── README.md                        (data dictionary)
│   ├── falconry_so_synthetic_baseline/  (Layer 1, 4,800 runs)
│   ├── falconry_so_pop_fe_sweep/        (Layer 1', 19,200 runs, 17,600 unique)
│   ├── tsp/                             (Layer 2, ~459 runs)
│   ├── gh_native_synthetic/             (Layer 3, ~1,200 runs canvas)
│   ├── ado_so_falconry/                 (Layer 4a, 990 runs)
│   ├── mo_zorn_ado_canvas/              (Layer 4b, ~1,100 runs incl. Campaign A/B/sweep/XC)
│   ├── cross_zdt_canvas/                (Layer 4c, 750 runs)
│   ├── falconry_zdt_validation/         (Layer 4d, 1,620 runs)
│   └── k3d_kakamigahara_D85/            (Layer 5, 166 runs incl. N=5+N=10+SS3+30-min)
├── surrogate/
│   └── README.md                        (Ambrosini GBR+ANN v2 — Q_tot, K_h, DF)
├── falconry/                            (v1.1 phase — post-publication)
├── grasshopper_assets/                  (v1.1 phase — post-publication)
├── figures_source_data/                 (per-figure underlying numbers)
└── scripts/
    └── README.md                        (surrogate training + learning curves)
```

---

## Data dictionary — common CSV schema

All per-run CSV files share a common header schema for uniform parsing:

```
run_id, layer, algorithm, problem, D, pop, FE, run_idx, seed,
fitness_best, fitness_mean, fitness_std, fitness_worst, fitness_median,
HV, IGD, PF_size, time_seconds, fe_consumed, terminated_by, notes
```

For multi-objective layers, the `fitness_*` fields are replaced by per-objective vectors and the `HV` / `IGD` / `PF_size` / `Spacing` / `Spread` / `Contribution_pct` columns become the primary metrics. See `data/README.md` for the per-layer dictionary.

---

## Reproducibility manifest

A `MANIFEST.md` at the root of this package lists every file with SHA256 checksum, byte size, and the section of the paper that depends on it. Reviewers can verify the integrity of the package by recomputing the SHA256 of any file and comparing it against the manifest.

To recompute (on macOS / Linux):

```bash
shasum -a 256 data/*/*.csv surrogate/*.json > _manifest_check.txt
diff <(awk '{print $2, $1}' _manifest_check.txt | sort) <(awk '/^- `/{print $2, $4}' MANIFEST.md | tr -d '`,' | sort)
```

(empty diff = package intact).

---

## Cite this package

If you use this package in your own work, please cite the paper and the package separately:

```
Ambrosini, L. (2026). SilverHawk: Metaheuristic Optimization for Architectural
Design Under Severe Computational Budget Constraints. Automation in Construction,
[volume]:[pages], doi:[TBD].

Ambrosini, L. (2026). SilverHawk Benchmark Replication Package
[Data set]. Zenodo. https://github.com/lucianoambrosini/silverhawk-benchmark
doi:10.5281/zenodo.20630810 (concept DOI — always resolves to the latest version)
```

---

## Licence

- **Data and surrogate models:** CC-BY 4.0 (free to use with attribution).
- **Source code (Falconry, scripts):** MIT licence.
- **Grasshopper files containing Pugnale K3D geometry:** redistributed with attribution per the original author's terms (Pugnale & Sassone 2007); see `grasshopper_assets/LICENSE_PUGNALE.md` for details once the file is released in Phase 2.

---

*Last updated: 2026-05-31. Status: v1.0-rc. Population schedule: pre-submit (data/surrogate/scripts), post-acceptance (manifest finalisation, repository DOI), post-publication (falconry binary + grasshopper assets).*

---

## SHARE build notes (Phase 1, peer-review)

This is the **trimmed, shareable** build of the replication package:

- **`data/`** — per-run benchmark CSVs shipped as **one ZIP per layer** (~3,660 CSV total).
  Superseded pre-bugfix runs (`pre_FIX/`) and all derived plots (`*.png`, `*.pdf`) are
  excluded. Unzip a layer to obtain its original per-solver/per-run folder structure.
- **`figures_source_data/`** — the 8 per-figure tables (numbering matches the revised
  manuscript v7.x / Supplementary v1.x); see its README for the figure mapping.
- **`surrogate/`**, **`scripts/`** — complete (Ambrosini GBR + ANN v2 models, training
  report, learning curves; figure/surrogate scripts).
- **Excluded from this build:** the paper figures (`figures/`, published with the article), the Falconry C# console source, and the Grasshopper `.gh`
  assets — the latter two ship in **Phase 2** after the SilverHawk food4Rhino release.
- **`MANIFEST.md`** lists every file with byte size and SHA256 for integrity checking.

**Before publishing:** fill the placeholders in this README (repository URL/DOI, author
e-mail, ORCID) and tag the version at journal acceptance.

# Multi-objective benchmark (MO)

[![DOI](https://img.shields.io/badge/DOI-10.5281%2Fzenodo.23157761-1682D4)](https://doi.org/10.5281/zenodo.23157761)
[![Status](https://img.shields.io/badge/paper-under_review-informational)]()
[![Data license: CC BY 4.0](https://img.shields.io/badge/data-CC%20BY%204.0-blue.svg)](https://creativecommons.org/licenses/by/4.0/)
[![Code license: MIT](https://img.shields.io/badge/code-MIT-green.svg)](https://opensource.org/licenses/MIT)

**Companion to:** *"Same algorithm, different answers: implementation, budget and reporting effects in surrogate-assisted multi-objective building design"* (L. Ambrosini, 2026, manuscript under review).

**Archive:** https://doi.org/10.5281/zenodo.23157761 — version 2.0 (concept DOI 10.5281/zenodo.23157760, which always resolves to the latest version). Cite the version DOI until the paper is published.

**Maintainer:** Luciano Ambrosini — luciano.ambrosini@outlook.com · ORCID 0000-0003-1529-2694

## What the package contains

Emulator models of the Zorn et al. (2025) shoebox-office surrogate (22 variables; objectives Q_tot, K_h minimized and DF maximized), all raw run logs, processed results, ZDT transfer checks, analysis and figure scripts, and the Grasshopper definition of the campaign.

- 18 optimizer configurations at three budget allocations of 5,000 evaluations (20 × 250, 40 × 125, 100 × 50): SilverHawk configurations, Opossum, WallaceiX, and canonical library baselines (pymoo 0.6.2 NSGA-II and SMS-EMOA, pymoode 0.3.0 GDE3).
- A NumPy inferencer of the emulator, identical to the Grasshopper component to within 1e-12 on the logged evaluations.
- Design-oriented analysis, robustness checks, Sobol sensitivity analysis, ZDT1–4 and ZDT6 results.

## Files on Zenodo

The archive is split into eight zip files plus `SHA256.txt`. Download all parts and unzip them into one folder to recover the full tree.

| Part | Content |
|---|---|
| `SH_MO_00_core` | README, models, processed results, scripts, figures, ZDT, Grasshopper definition |
| `SH_MO_01_raw_canvas` | Canvas exports (SilverHawk, Opossum, WallaceiX) |
| `SH_MO_02_console_p20_i250`, `_p40_i125`, `_p100_i50` | Seeded console runs per allocation |
| `SH_MO_03_library_NSGA-II`, `_SMS-EMOA`, `_GDE3` | Library baseline runs |

## Benchmark problem

Zorn et al. (2025), *Energy and Buildings* 336, 115562, https://doi.org/10.1016/j.enbuild.2025.115562. Original data: https://doi.org/10.18419/darus-4532 (not redistributed here).

## Licence

Data and models: CC BY 4.0. Scripts: MIT.

[← Back to index](../README.md)

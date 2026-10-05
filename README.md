# Replication package — Same algorithm, different answers: implementation, budget and reporting effects in surrogate-assisted multi-objective building design

Version 2.0. Data, emulator models and analysis scripts for the manuscript by L. Ambrosini (2026, under review).

Benchmark problem: Zorn et al. (2025), Energy and Buildings 336, 115562, https://doi.org/10.1016/j.enbuild.2025.115562. Original data: https://doi.org/10.18419/darus-4532 (not redistributed here).

## What is new in version 2.0

- Canonical library configurations (pymoo 0.6.2 NSGA-II and SMS-EMOA, pymoode 0.3.0 GDE3; library defaults) on the same emulator: every evaluation of 3 allocations × 30 runs (`library_runs/`).
- A NumPy inferencer of the emulator (`models/inferencer_numpy/emu.py`), identical to the Grasshopper component to within 1e-12 on the logged console evaluations.
- Design-oriented analysis (lowest energy demand under overheating and daylight targets), robustness checks (DF clipped at zero, alternative reference point, IGD+ without SilverHawk points), Sobol sensitivity analysis, contrasts between implementations (`scripts_v2/`, `processed_v2/`).
- ZDT1–4 and ZDT6 results (D = 10, 10,000 evaluations): Grasshopper campaign of April–May 2026 (per-function summaries), library configurations, and seeded console runs (`zdt/`).
- Script names harmonised (`mo_*.py`). Data of version 1.0 are unchanged.

## Contents

| Folder | Content |
|---|---|
| `raw/canvas/<allocation>/SilverHawk/<configuration>/` | SilverHawk canvas exports (CSV): metadata header, convergence trace, final population, cumulative non-dominated archive. Runs 1–5 are the primary data; at 100 × 50, runs 6–10 of some configurations are used only in a sensitivity check. |
| `raw/canvas/<allocation>/Opossum_MO/<algorithm>/` | Opossum 3.1.2 evaluation logs (every evaluation: parameters and objectives). |
| `raw/canvas/<allocation>/WallaceiX/` | WallaceiX 2.7 evaluation logs (CSV). |
| `raw/console/<allocation>/` | Headless-console runs of the SilverHawk configurations (in-house development console, not distributed; same algorithm code and emulator as the plug-in): every evaluation in order (`*_evals.csv`) and final set (`*_final.csv`), ten runs per configuration, seed = 5000 + 137·r. |
| `raw/opossum_3.2.1/`, `raw/supplementary_runs/` | Opossum 3.2.1 block (RBFMOpt, TPE, MADS, HypE) and the single extended RBFMOpt / HypE runs. |
| `library_runs/` | Canonical library configurations: `<algorithm>_p<pop>_run<r>_evals.csv` (every evaluation: objectives and variables, binaries rounded) and `_final.csv` (final population), seed = 5000 + 137·(r − 1). |
| `models/json_models/`, `models/training_metadata.json` | Emulator models (scikit-learn exports to JSON) and their training metadata and accuracy. |
| `models/inferencer_numpy/emu.py` | NumPy inferencer of the JSON models (the DF model predicts −DF; binaries x19–x22 are rounded). |
| `processed/` | Per-run indicators and statistics of version 1.0 (tool configurations). |
| `processed_v2/` | Results of version 2.0: per-run HV including library runs (`a1_hv_runs.csv`), robustness (`a2_robust_runs.csv`), design targets (`a3_physical_runs.csv`, `a6_phys_table.csv`), front composition (`a4_front_p40.csv`), Sobol indices (`a4_sobol.csv`), library summary (`a5_baseline_table.csv`), contrasts (`a7_contrasts.csv`), ZDT tables. |
| `zdt/` | `gh_canvas/`: per-function summaries of the Grasshopper ZDT campaign and the metric scripts (`mo_metrics.py`, `mo_cross_zdt.py`); `library/`: library configurations on ZDT; `console/`: seeded console runs (30 runs) and their summaries. The raw Grasshopper ZDT logs are available from the author on request. |
| `grasshopper/` | Grasshopper definition of the campaign (requires Rhinoceros 8, the SilverHawk plug-in, and Opossum and WallaceiX for their components). |
| `scripts/`, `scripts_v2/` | Analysis and figure scripts (Python 3; NumPy, pandas, SciPy, pymoo, pymoode, SALib, matplotlib). |

Allocations (population × generations, 5,000 evaluations): `p20_i250` = 20 × 250, `p40_i125` = 40 × 125, `p100_i50` = 100 × 50.

Objectives: Q_tot [kWh/(m²·a)] and K_h [K·h/a] minimized, DF [–] maximized; hypervolume is computed on (Q_tot, K_h, −DF) with the reference point r = (58.2017, 2228.382, 0.080245).

Variable order in all logs: x1–x15 shading rows 1–5 (X, Y, Z; Z in [0, 0.5]), x16 window sill height [0, 1], x17 night-time air-change rate [0, 5], x18 insulation thickness [0, 0.49] m, x19–x22 binary choices.

## Reproducing the results

Version 1.0 analysis (tool configurations), from a folder containing `results/` (copy `processed/` to `results/` to start from the released values):

```
python scripts/mo_analysis.py raw/canvas processed
python scripts/mo_stats.py processed
python scripts/mo_tiers.py
```

Version 2.0 analysis (run from `scripts_v2/`; paths are relative to the package root):

```
python baselines.py ../library_runs NSGA-II,SMS-EMOA,GDE3 20,40,100 30   # regenerates library_runs/ (same seeds)
python a1_hv.py; python a2_robust.py; python a3_physical.py; python a4_design.py
python a5_baseline_stats.py; python a6_phys_table.py; python a7_contrasts.py
python zdt_baselines.py
python fig3.py; python fig_time_impl.py; python fig_design.py; python fig_sobol.py; python fig_zdt.py   # figures to figures_v2/
```

## Software

SilverHawk 0.6 series (campaign builds 0.6.28–0.6.29; ZDT campaign 0.6.27, differing only in the user interface) for Grasshopper / Rhinoceros 8 SR35, a free plug-in that contains the benchmark component and the SilverHawk configurations; Opossum 3.1.2 and 3.2.1; WallaceiX 2.7; pymoo 0.6.2; pymoode 0.3.0. Hardware of the Grasshopper runs: Intel Core i7-4770K, 32 GB RAM, Windows.

## Licence

Data and models: CC BY 4.0. Scripts: MIT.

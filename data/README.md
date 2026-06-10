# Replication Data — Per-Layer Dictionary

This folder contains the per-run raw output of all five benchmark layers reported in the paper. Each sub-folder corresponds to one layer of the benchmark protocol and contains one or more CSV files.

## Common schema

All CSV files share a common header set, extended per layer where additional metrics apply:

| Column | Type | Description |
|--------|------|-------------|
| `run_id` | string | Unique identifier `{layer}_{algorithm}_{problem}_{D}_{seed}` |
| `layer` | string | One of: L1, L1p, L2, L3, L4a, L4b, L4c, L4d, L5 |
| `algorithm` | string | Solver name (canonical, e.g., `MERLIN`, `Opossum-RBFOpt`) |
| `problem` | string | Problem identifier (e.g., `Rastrigin`, `TSP20`, `Q_tot`, `ZDT4`, `K3D_Kakamigahara`) |
| `D` | int | Dimensionality |
| `pop` | int | Population size |
| `FE` | int | Total FE budget |
| `run_idx` | int | Run index (0-based, within campaign) |
| `seed` | int | MersenneTwister seed (canonical: `5000 + run_idx × 137`) |
| `fitness_best` | float | Best fitness at termination |
| `fitness_mean` | float | Mean fitness of final population |
| `fitness_std` | float | Std fitness of final population |
| `fitness_worst` | float | Worst fitness of final population |
| `fitness_median` | float | Median fitness of final population |
| `time_seconds` | float | Wall-clock time elapsed |
| `fe_consumed` | int | Actual FE consumed (may be less than budget for early termination) |
| `terminated_by` | string | One of: `budget`, `wall_clock`, `stagnation`, `manual` |
| `notes` | string | Optional free-text notes (e.g., RBFMOpt budget exception) |

## Multi-objective extension columns

For Layer 4b (MO Zorn ADO), Layer 4c (Cross-ZDT), Layer 4d (Falconry ZDT validation):

| Column | Type | Description |
|--------|------|-------------|
| `HV` | float | Hypervolume (Beume 2009 exact slice-sweep, per-run auto-reference 1.1×) |
| `IGD` | float | Inverted generational distance (against analytical PF for ZDT, against best-known cumulative archive for ADO) |
| `PF_size` | int | Pareto-front size (cumulative ExternalArchive) |
| `Spacing` | float | Spacing metric (Schott 1995) |
| `Spread` | float | Spread / delta metric (Deb 2001) |
| `Contribution_pct` | float | Contribution percentage to merged-front HV |
| `pareto_front_csv` | string | Filename of separate CSV listing the per-run PF objective vectors |

The `pareto_front_csv` files live in a sibling sub-folder named `pareto_fronts/` within each Layer 4 directory.

## K3D Kakamigahara extension columns (Layer 5)

| Column | Type | Description |
|--------|------|-------------|
| `displacement_cm` | float | Maximum nodal displacement under self-weight (the fitness) |
| `feasible` | bool | Whether the result satisfies the L/300 ≈ 3 cm feasibility threshold |
| `convergence_25` | float | Fitness at 25% wall-clock checkpoint |
| `convergence_50` | float | Fitness at 50% wall-clock checkpoint |
| `convergence_75` | float | Fitness at 75% wall-clock checkpoint |
| `convergence_100` | float | Fitness at 100% wall-clock checkpoint |

## Smart Start columns (Layer 5 SS=3 probe + intra-solver records)

| Column | Type | Description |
|--------|------|-------------|
| `ss_seeds_used` | int | Number of warmup seed initializations (1, 3, or 5) |
| `ss_alpha` | float | Composite-score weight (default 0.15) |
| `ss_early_stop_seeds` | int | Seeds terminated by early-stop mechanism |
| `ss_winning_seed_idx` | int | Index of the seed selected for exploitation phase |

## Cross-references with paper sections

See `replication_package/MANIFEST.md` for the per-file map to the paper section / table that depends on it.

## Population schedule

- **Phase 1 (pre-submit):** L4 ADO MO + L5 K3D + L4a ADO SO Falconry are top priority (highest impact for peer review).
- **Phase 1 cont.:** L1, L1', L2, L3 in order of size manageability.
- **Phase 2 (post-publication):** L4c Cross-ZDT canvas, L4d Falconry ZDT (may be released alongside SilverHawk plugin if the GH cross-ZDT components are part of the toolset).

---

*Last updated: 2026-05-31 — v1.0-rc.*

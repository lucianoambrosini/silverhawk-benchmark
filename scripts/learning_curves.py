"""
PaperA — Learning curves for surrogate overfitting diagnosis (P-07)
================================================================

Purpose: check whether the GBR (Q_tot, DF) and MLP (K_h) surrogates
trained on Zorn et al. 2025 LHS dataset show a train/CV R² divergence
consistent with overfitting.

Protocol (replicates §6.4.1 of the paper):
- Input: LHS_01.json (975 Latin Hypercube samples, 22 features, 3 objectives)
- IQR-based outlier removal on the 3 objectives (target: ~874 retained)
- StandardScaler on features
- GBR optimal config for Q_tot: n_estimators=300, max_depth=3,
  min_samples_leaf=1, min_samples_split=5
- GBR for DF: same config (refit with grid search if time permits)
- MLP (64-32-16, ReLU, Adam) for K_h
- sklearn.model_selection.learning_curve, 5-fold CV, train_sizes
  = [0.2, 0.35, 0.5, 0.65, 0.8, 1.0]
- Output: 3 PNG + 1 CSV + 1 interpretation note

Usage:
    python PaperA_learning_curves.py [--data PATH_TO_LHS.json] [--outdir DIR]

If no arguments given: uses defaults below.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.neural_network import MLPRegressor
from sklearn.model_selection import learning_curve, KFold
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline


# --------------------------------------------------------------------------- #
# Defaults
# --------------------------------------------------------------------------- #

DEFAULT_DATA = Path(
    "/sessions/elegant-vigilant-feynman/zorn/Benchmark_Data/BPS_Random/LHS_00.json"
)
DEFAULT_OUTDIR = Path(
    "/sessions/elegant-vigilant-feynman/mnt/SilverHawk new evolutionary solver"
)

TRAIN_SIZES = np.array([0.2, 0.35, 0.5, 0.65, 0.8, 1.0])
CV_FOLDS = 5
RANDOM_STATE = 42

# Paper config (§6.4.1): optimal GBR hyperparameters identified via grid search
GBR_PARAMS = dict(
    n_estimators=300,
    max_depth=3,
    min_samples_leaf=1,
    min_samples_split=5,
    random_state=RANDOM_STATE,
)

# Paper config (§6.4.1): ANN 64-32-16, ReLU, Adam
MLP_PARAMS = dict(
    hidden_layer_sizes=(64, 32, 16),
    activation="relu",
    solver="adam",
    max_iter=500,
    random_state=RANDOM_STATE,
    early_stopping=False,
)


# --------------------------------------------------------------------------- #
# Data loading
# --------------------------------------------------------------------------- #

def load_lhs(path: Path) -> pd.DataFrame:
    """Load LHS JSON (Zorn dataset) into a DataFrame.

    Supports two schemas:
    - BPS_Random/LHS_00.json: dict keyed by UUID → {objectives, time, params}
      (975 samples — the actual training set per Zorn §3.4 and paper §6.4.1)
    - SuMo_Random/LHS_01.json: list of {params, time, objectives}
      (10 001 samples — surrogate-evaluated LHS, NOT used for training)

    Note on DF sign: Zorn encodes DF as negative (minimisation convention).
    The paper reports DF as maximise-direction positive. We flip sign here
    so DF ≥ 0 and the surrogate is trained on the paper's convention.
    """
    raw = json.loads(path.read_text(encoding="utf-8"))

    if isinstance(raw, dict):
        entries = raw.values()  # BPS_Random UUID-keyed
    elif isinstance(raw, list):
        entries = raw  # SuMo_Random list-based
    else:
        raise ValueError(f"Unexpected JSON schema: {type(raw)}")

    rows = []
    for entry in entries:
        row = dict(entry["params"])
        row["Q_tot"] = entry["objectives"]["Q_tot"]
        row["K_h"] = entry["objectives"]["Kh"]
        row["DF"] = -entry["objectives"]["DF"]  # flip sign
        rows.append(row)
    return pd.DataFrame(rows)


def iqr_outlier_filter(df: pd.DataFrame, objectives: list[str]) -> pd.DataFrame:
    """IQR-based outlier filter on each objective (per-obj union-removal)."""
    mask = np.ones(len(df), dtype=bool)
    for col in objectives:
        q1, q3 = df[col].quantile([0.25, 0.75])
        iqr = q3 - q1
        lo, hi = q1 - 1.5 * iqr, q3 + 1.5 * iqr
        mask &= df[col].between(lo, hi)
    filtered = df.loc[mask].reset_index(drop=True)
    return filtered


# --------------------------------------------------------------------------- #
# Learning curve
# --------------------------------------------------------------------------- #

def fit_learning_curve(
    estimator,
    X: np.ndarray,
    y: np.ndarray,
    objective_name: str,
) -> pd.DataFrame:
    """Compute learning curve and return a tidy DataFrame."""
    pipeline = Pipeline([("scaler", StandardScaler()), ("model", estimator)])
    cv = KFold(n_splits=CV_FOLDS, shuffle=True, random_state=RANDOM_STATE)

    train_sizes_abs, train_scores, cv_scores = learning_curve(
        estimator=pipeline,
        X=X,
        y=y,
        train_sizes=TRAIN_SIZES,
        cv=cv,
        scoring="r2",
        n_jobs=1,  # sequential: more predictable memory footprint on sandbox
        random_state=RANDOM_STATE,
        shuffle=True,
    )

    return pd.DataFrame(
        {
            "objective": objective_name,
            "train_size": train_sizes_abs,
            "train_R2_mean": train_scores.mean(axis=1),
            "train_R2_std": train_scores.std(axis=1),
            "cv_R2_mean": cv_scores.mean(axis=1),
            "cv_R2_std": cv_scores.std(axis=1),
            "gap": train_scores.mean(axis=1) - cv_scores.mean(axis=1),
        }
    )


# --------------------------------------------------------------------------- #
# Plotting
# --------------------------------------------------------------------------- #

def plot_curve(lc: pd.DataFrame, title: str, outpath: Path) -> None:
    fig, ax = plt.subplots(figsize=(7, 4.5))

    ax.plot(lc["train_size"], lc["train_R2_mean"], "o-", label="Train R²",
            color="#1f77b4", linewidth=2)
    ax.fill_between(
        lc["train_size"],
        lc["train_R2_mean"] - lc["train_R2_std"],
        lc["train_R2_mean"] + lc["train_R2_std"],
        alpha=0.15, color="#1f77b4",
    )

    ax.plot(lc["train_size"], lc["cv_R2_mean"], "s-", label="5-fold CV R²",
            color="#d62728", linewidth=2)
    ax.fill_between(
        lc["train_size"],
        lc["cv_R2_mean"] - lc["cv_R2_std"],
        lc["cv_R2_mean"] + lc["cv_R2_std"],
        alpha=0.15, color="#d62728",
    )

    # Annotate final gap
    final = lc.iloc[-1]
    gap = final["gap"]
    ax.annotate(
        f"Final gap = {gap:.3f}\n(train={final['train_R2_mean']:.3f}, "
        f"CV={final['cv_R2_mean']:.3f})",
        xy=(final["train_size"], final["cv_R2_mean"]),
        xytext=(0.55, 0.15),
        textcoords="axes fraction",
        fontsize=9,
        bbox=dict(boxstyle="round,pad=0.4", facecolor="wheat", alpha=0.85),
        arrowprops=dict(arrowstyle="->", color="gray"),
    )

    ax.set_xlabel("Training samples (n)")
    ax.set_ylabel("R²")
    ax.set_title(title)
    ax.set_ylim(-0.1, 1.05)
    ax.grid(True, alpha=0.3)
    ax.legend(loc="lower right")
    fig.tight_layout()
    fig.savefig(outpath, dpi=200, bbox_inches="tight")
    plt.close(fig)


# --------------------------------------------------------------------------- #
# Interpretation
# --------------------------------------------------------------------------- #

def interpret(final_row: pd.Series, obj_name: str, paper_cv_r2: float) -> str:
    gap = final_row["gap"]
    cv_r2 = final_row["cv_R2_mean"]
    train_r2 = final_row["train_R2_mean"]

    if gap < 0.05:
        verdict = "NO OVERFITTING (gap < 0.05)"
    elif gap < 0.10:
        verdict = "MILD OVERFITTING (0.05 ≤ gap < 0.10)"
    elif gap < 0.20:
        verdict = "MODERATE OVERFITTING (0.10 ≤ gap < 0.20)"
    else:
        verdict = "STRONG OVERFITTING (gap ≥ 0.20)"

    match = "CONSISTENT" if abs(cv_r2 - paper_cv_r2) < 0.05 else "DIVERGENT from paper"

    return (
        f"### {obj_name}\n\n"
        f"- Train R² (at n={int(final_row['train_size'])}): **{train_r2:.3f}**\n"
        f"- CV R² (at n={int(final_row['train_size'])}): **{cv_r2:.3f}** "
        f"(paper reports {paper_cv_r2:.3f} → {match})\n"
        f"- Train–CV gap: **{gap:.3f}** → **{verdict}**\n\n"
    )


# --------------------------------------------------------------------------- #
# Main
# --------------------------------------------------------------------------- #

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=DEFAULT_DATA)
    parser.add_argument("--outdir", type=Path, default=DEFAULT_OUTDIR)
    args = parser.parse_args()

    print(f"Loading LHS dataset from: {args.data}")
    df = load_lhs(args.data)
    print(f"  Loaded {len(df)} samples, {df.shape[1] - 3} features + 3 objectives")

    df_clean = iqr_outlier_filter(df, ["Q_tot", "K_h", "DF"])
    print(f"  After IQR outlier removal: {len(df_clean)} samples "
          f"({len(df) - len(df_clean)} removed)")

    feature_cols = [c for c in df_clean.columns if c not in ("Q_tot", "K_h", "DF")]
    X = df_clean[feature_cols].values
    print(f"  Feature matrix shape: {X.shape}")
    args.outdir.mkdir(parents=True, exist_ok=True)

    specs = [
        (
            "Q_tot",
            GradientBoostingRegressor(**GBR_PARAMS),
            "GBR (n_est=300, max_d=3, min_leaf=1, min_split=5)",
            0.964,
        ),
        (
            "DF",
            GradientBoostingRegressor(**GBR_PARAMS),
            "GBR (same hyperparameters)",
            0.780,
        ),
        (
            "K_h",
            MLPRegressor(**MLP_PARAMS),
            "MLP (64-32-16, ReLU, Adam)",
            0.931,
        ),
    ]

    all_curves = []
    interpretation = [
        "# Learning curves — surrogate overfitting diagnosis (P-07)\n\n",
        f"Dataset: `LHS_01.json` · Samples before IQR: {len(df)} · ",
        f"After IQR: {len(df_clean)} · Features: {X.shape[1]}\n\n",
        f"CV: {CV_FOLDS}-fold KFold (shuffle=True, random_state={RANDOM_STATE})\n\n",
        f"Train sizes tested: {TRAIN_SIZES.tolist()}\n\n",
        "---\n\n",
    ]

    for obj, estimator, model_label, paper_r2 in specs:
        print(f"\n== Fitting learning curve for {obj} ({model_label}) ==", flush=True)
        t0 = time.time()
        y = df_clean[obj].values
        lc = fit_learning_curve(estimator, X, y, obj)
        print(f"  elapsed: {time.time() - t0:.1f}s", flush=True)
        all_curves.append(lc)

        plot_path = args.outdir / f"learning_curve_{obj}.png"
        plot_curve(
            lc,
            f"Learning curve — {obj}  |  {model_label}",
            plot_path,
        )
        print(f"  → {plot_path.name}")

        interpretation.append(interpret(lc.iloc[-1], obj, paper_r2))

    curves_df = pd.concat(all_curves, ignore_index=True)
    csv_path = args.outdir / "learning_curve_summary.csv"
    curves_df.to_csv(csv_path, index=False)
    print(f"\nSummary CSV → {csv_path.name}")

    note_path = args.outdir / "learning_curve_interpretation.md"
    note_path.write_text("".join(interpretation), encoding="utf-8")
    print(f"Interpretation note → {note_path.name}")

    print("\nDone.")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        raise

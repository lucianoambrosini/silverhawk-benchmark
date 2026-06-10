"""
Ambrosini Surrogate v2 — training pipeline for the 10k SuMo dataset.
===================================================================

Purpose: produce an enhanced surrogate for ADO D=22 by training on the
full 10 001-sample SuMo_Random/LHS_01.json dataset (vs. the 975-sample
BPS_Random/LHS_00.json used in v1 and in Zorn 2025). Expected payoffs:

- Q_tot CV R²:  0.964 (v1) → ~0.991 (v2)
- DF    CV R²:  0.780 (v1) → ~0.982 (v2)   [MAIN WIN: DF overfitting gone]
- K_h   CV R²:  0.931 (v1) → ~0.998 (v2)

Outputs (written to ./models_v2/):
  gbr_qtot_v2.json    — Sklearn GBR in SH_BenchmarkADO-compatible schema
  gbr_df_v2.json      — idem
  ann_kh_v2.json      — Sklearn MLP in SH_BenchmarkADO-compatible schema
  scaler_v2.json      — StandardScaler mean/scale + feature_names
  training_report_v2.md — accuracy summary + grid-search winner + learning curve

Usage:
  python train_surrogate_v2.py [--data PATH] [--outdir DIR] [--grid-search]
  --grid-search: re-run full 81-config GBR grid (default: use v1 winners)
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.neural_network import MLPRegressor
from sklearn.model_selection import GridSearchCV, KFold, cross_val_score, learning_curve
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import r2_score, mean_squared_error


# --------------------------------------------------------------------------- #
# Defaults
# --------------------------------------------------------------------------- #

DEFAULT_DATA = Path("SuMo_Random/LHS_01.json")  # relative; use --data to override
DEFAULT_OUTDIR = Path("./models_v2")

CV_FOLDS = 5
RANDOM_STATE = 42

# v1 grid-search winner — use as default (skip grid-search unless --grid-search)
V1_GBR_PARAMS = dict(
    n_estimators=300,
    max_depth=3,
    min_samples_leaf=1,
    min_samples_split=5,
)

# Full 81-config grid (Zorn/Ambrosini protocol)
GBR_GRID = {
    "model__n_estimators": [100, 200, 300],
    "model__max_depth": [3, 5, 7],
    "model__min_samples_split": [2, 5, 10],
    "model__min_samples_leaf": [1, 2, 4],
}

MLP_PARAMS = dict(
    hidden_layer_sizes=(64, 32, 16),
    activation="relu",
    solver="adam",
    max_iter=1000,             # higher than v1 (500) — more data needs more iters
    early_stopping=True,        # on 10k data, use early stopping
    validation_fraction=0.1,
    n_iter_no_change=20,
    random_state=RANDOM_STATE,
)


# --------------------------------------------------------------------------- #
# Data
# --------------------------------------------------------------------------- #

def load_lhs(path: Path) -> pd.DataFrame:
    """Load either dict-keyed (BPS_Random) or list (SuMo_Random) LHS JSON."""
    raw = json.loads(path.read_text(encoding="utf-8"))
    entries = raw.values() if isinstance(raw, dict) else raw

    rows = []
    for e in entries:
        r = dict(e["params"])
        r["Q_tot"] = e["objectives"]["Q_tot"]
        r["K_h"] = e["objectives"]["Kh"]
        r["DF"] = -e["objectives"]["DF"]  # flip sign to paper convention
        rows.append(r)
    return pd.DataFrame(rows)


def iqr_filter(df: pd.DataFrame, objectives: list[str]) -> pd.DataFrame:
    """Per-obj union-removal IQR outlier filter (replicates v1 / Zorn §3.4)."""
    mask = np.ones(len(df), dtype=bool)
    for col in objectives:
        q1, q3 = df[col].quantile([0.25, 0.75])
        iqr = q3 - q1
        lo, hi = q1 - 1.5 * iqr, q3 + 1.5 * iqr
        mask &= df[col].between(lo, hi)
    return df.loc[mask].reset_index(drop=True)


# --------------------------------------------------------------------------- #
# GBR → SH JSON serialiser
# --------------------------------------------------------------------------- #

def gbr_to_json(gbr: GradientBoostingRegressor) -> dict:
    """Serialise sklearn GBR in the exact schema used by SH_BenchmarkADO C#."""
    trees = []
    for est_arr in gbr.estimators_:
        tree = est_arr[0].tree_
        feat = tree.feature.tolist()
        thr = tree.threshold.tolist()
        cl = tree.children_left.tolist()
        cr = tree.children_right.tolist()
        # sklearn stores value with shape (n_nodes, n_outputs, n_classes)
        # for regression, n_outputs=n_classes=1 → squeeze to scalar per node
        val = tree.value.reshape(tree.node_count, -1).tolist()
        trees.append({
            "feature": feat,
            "threshold": thr,
            "children_left": cl,
            "children_right": cr,
            "value": val,
            "n_nodes": int(tree.node_count),
        })

    # sklearn GBR init is DummyRegressor; its prediction is the mean of y
    # Access via .init_.constant_ (older sklearn) or .init_.constants_[0]
    try:
        init_val = float(gbr.init_.constant_)
    except AttributeError:
        init_val = float(gbr.init_.constants_[0])

    return {
        "type": "GBR",
        "n_estimators": int(gbr.n_estimators),
        "learning_rate": float(gbr.learning_rate),
        "init_value": init_val,
        "trees": trees,
    }


# --------------------------------------------------------------------------- #
# MLP → SH JSON serialiser
# --------------------------------------------------------------------------- #

def mlp_to_json(mlp: MLPRegressor) -> dict:
    """Serialise sklearn MLP in the SH_BenchmarkADO layers schema."""
    layers = []
    for W, b in zip(mlp.coefs_, mlp.intercepts_):
        layers.append({
            "weights": W.tolist(),
            "biases": b.tolist(),
            "n_in": int(W.shape[0]),
            "n_out": int(W.shape[1]),
        })
    return {
        "type": "ANN",
        "activation": str(mlp.activation),
        "n_layers": len(layers),
        "layers": layers,
        "out_activation": str(mlp.out_activation_),
    }


def scaler_to_json(scaler: StandardScaler, feature_names: list[str]) -> dict:
    return {
        "mean": scaler.mean_.tolist(),
        "scale": scaler.scale_.tolist(),
        "feature_names": feature_names,  # NEW: explicit (v1 omitted this)
    }


# --------------------------------------------------------------------------- #
# Training
# --------------------------------------------------------------------------- #

def train_gbr(
    X: np.ndarray, y: np.ndarray, feature_names: list[str],
    scaler_fit_X: np.ndarray, do_grid: bool, cv, label: str,
):
    """Fit GBR (optionally with grid search), wrapped with scaler.

    Returns fitted unscaled GBR, fitted scaler, CV R², train R², best params.
    """
    t0 = time.time()

    # Fit scaler on all X (so the serialised scaler is consistent)
    scaler = StandardScaler().fit(scaler_fit_X)
    X_scaled = scaler.transform(X)

    if do_grid:
        print(f"  [{label}] grid search over {len(GBR_GRID['model__n_estimators']) * len(GBR_GRID['model__max_depth']) * len(GBR_GRID['model__min_samples_split']) * len(GBR_GRID['model__min_samples_leaf'])} configs...", flush=True)
        pipe = Pipeline([("model", GradientBoostingRegressor(random_state=RANDOM_STATE))])
        gs = GridSearchCV(pipe, GBR_GRID, cv=cv, scoring="r2", n_jobs=1, verbose=0)
        gs.fit(X_scaled, y)
        best_gbr = gs.best_estimator_.named_steps["model"]
        best_params = {k.replace("model__", ""): v for k, v in gs.best_params_.items()}
        cv_r2 = float(gs.best_score_)
    else:
        best_gbr = GradientBoostingRegressor(**V1_GBR_PARAMS, random_state=RANDOM_STATE)
        cv_scores = cross_val_score(best_gbr, X_scaled, y, cv=cv, scoring="r2", n_jobs=1)
        best_gbr.fit(X_scaled, y)
        best_params = V1_GBR_PARAMS
        cv_r2 = float(cv_scores.mean())

    train_r2 = float(r2_score(y, best_gbr.predict(X_scaled)))
    print(f"  [{label}] CV R² = {cv_r2:.4f}  Train R² = {train_r2:.4f}  "
          f"gap = {train_r2 - cv_r2:.4f}  ({time.time() - t0:.1f}s)", flush=True)
    return best_gbr, scaler, cv_r2, train_r2, best_params


def train_mlp(X: np.ndarray, y: np.ndarray, cv, label: str):
    t0 = time.time()
    scaler = StandardScaler().fit(X)
    X_scaled = scaler.transform(X)

    mlp = MLPRegressor(**MLP_PARAMS)
    cv_scores = cross_val_score(mlp, X_scaled, y, cv=cv, scoring="r2", n_jobs=1)
    mlp.fit(X_scaled, y)
    train_r2 = float(r2_score(y, mlp.predict(X_scaled)))
    cv_r2 = float(cv_scores.mean())
    print(f"  [{label}] CV R² = {cv_r2:.4f}  Train R² = {train_r2:.4f}  "
          f"gap = {train_r2 - cv_r2:.4f}  ({time.time() - t0:.1f}s)", flush=True)
    return mlp, scaler, cv_r2, train_r2


# --------------------------------------------------------------------------- #
# Main
# --------------------------------------------------------------------------- #

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=DEFAULT_DATA)
    parser.add_argument("--outdir", type=Path, default=DEFAULT_OUTDIR)
    parser.add_argument("--grid-search", action="store_true",
                        help="Re-run GBR grid search instead of using v1 winners")
    parser.add_argument("--learning-curves", action="store_true",
                        help="Also produce learning curves (adds ~5 min)")
    args = parser.parse_args()

    args.outdir.mkdir(parents=True, exist_ok=True)

    print(f"Loading: {args.data}")
    df = load_lhs(args.data)
    print(f"  Samples before IQR: {len(df)}")
    df_clean = iqr_filter(df, ["Q_tot", "K_h", "DF"])
    print(f"  Samples after IQR:  {len(df_clean)}")

    feature_cols = [c for c in df_clean.columns if c not in ("Q_tot", "K_h", "DF")]
    X = df_clean[feature_cols].values
    cv = KFold(n_splits=CV_FOLDS, shuffle=True, random_state=RANDOM_STATE)

    report_lines = [
        "# Surrogate Ambrosini v2 — Training Report\n\n",
        f"- Input dataset: `{args.data.name}` ({len(df)} samples)\n",
        f"- After IQR (union per-obj): {len(df_clean)} retained\n",
        f"- Features (n={len(feature_cols)}): {feature_cols}\n",
        f"- CV: {CV_FOLDS}-fold KFold (shuffle=True, random_state={RANDOM_STATE})\n",
        f"- GBR grid search: {'YES (81 configs)' if args.grid_search else 'NO (using v1 winners)'}\n\n",
        "## Accuracy summary\n\n",
        "| Objective | Model | CV R² | Train R² | Gap | Paper v1 CV R² | Δ vs v1 |\n",
        "|-----------|-------|:-----:|:--------:|:---:|:--------------:|:-------:|\n",
    ]
    paper_v1 = {"Q_tot": 0.964, "DF": 0.780, "K_h": 0.931}
    all_params = {}

    # Q_tot
    print("\n=== GBR Q_tot ===")
    y = df_clean["Q_tot"].values
    gbr_qtot, sc_qtot, cv_r2_q, tr_r2_q, p_q = train_gbr(
        X, y, feature_cols, X, args.grid_search, cv, "Q_tot"
    )
    (args.outdir / "gbr_qtot_v2.json").write_text(
        json.dumps(gbr_to_json(gbr_qtot), indent=2)
    )
    all_params["Q_tot"] = p_q

    # DF
    print("\n=== GBR DF ===")
    y = df_clean["DF"].values
    gbr_df, sc_df, cv_r2_d, tr_r2_d, p_d = train_gbr(
        X, y, feature_cols, X, args.grid_search, cv, "DF"
    )
    (args.outdir / "gbr_df_v2.json").write_text(
        json.dumps(gbr_to_json(gbr_df), indent=2)
    )
    all_params["DF"] = p_d

    # K_h
    print("\n=== MLP K_h ===")
    y = df_clean["K_h"].values
    mlp_kh, sc_kh, cv_r2_k, tr_r2_k = train_mlp(X, y, cv, "K_h")
    (args.outdir / "ann_kh_v2.json").write_text(
        json.dumps(mlp_to_json(mlp_kh), indent=2)
    )

    # Scaler (use Q_tot scaler — identical since fit on all X)
    (args.outdir / "scaler_v2.json").write_text(
        json.dumps(scaler_to_json(sc_qtot, feature_cols), indent=2)
    )

    # Report
    for obj, cv_r, tr_r in [
        ("Q_tot", cv_r2_q, tr_r2_q),
        ("DF",    cv_r2_d, tr_r2_d),
        ("K_h",   cv_r2_k, tr_r2_k),
    ]:
        model_lbl = "GBR" if obj != "K_h" else "MLP"
        delta = cv_r - paper_v1[obj]
        report_lines.append(
            f"| {obj} | {model_lbl} | **{cv_r:.4f}** | {tr_r:.4f} | "
            f"{tr_r - cv_r:.4f} | {paper_v1[obj]:.3f} | {delta:+.4f} |\n"
        )

    report_lines.append("\n## GBR hyperparameters used\n\n")
    for obj, p in all_params.items():
        report_lines.append(f"- **{obj}**: {p}\n")

    # Optional: learning curves
    if args.learning_curves:
        print("\n=== Learning curves ===")
        report_lines.append("\n## Learning curves (5-fold CV)\n\n")
        for obj in ["Q_tot", "DF", "K_h"]:
            y = df_clean[obj].values
            est = (GradientBoostingRegressor(**V1_GBR_PARAMS, random_state=RANDOM_STATE)
                   if obj != "K_h" else MLPRegressor(**MLP_PARAMS))
            pipe = Pipeline([("s", StandardScaler()), ("m", est)])
            ts, tr, cv_s = learning_curve(
                pipe, X, y,
                train_sizes=np.array([0.2, 0.4, 0.6, 0.8, 1.0]),
                cv=cv, scoring="r2", n_jobs=1, shuffle=True, random_state=RANDOM_STATE,
            )
            gap_final = tr.mean(axis=1)[-1] - cv_s.mean(axis=1)[-1]
            report_lines.append(
                f"- **{obj}**: final gap at n={int(ts[-1])} = {gap_final:.3f}\n"
            )
            print(f"  {obj}: final gap = {gap_final:.4f}")

    (args.outdir / "training_report_v2.md").write_text(
        "".join(report_lines), encoding="utf-8"
    )

    print(f"\nAll artefacts written to {args.outdir.resolve()}")
    print("Files:")
    for f in sorted(args.outdir.iterdir()):
        print(f"  {f.name}  ({f.stat().st_size} bytes)")


if __name__ == "__main__":
    main()

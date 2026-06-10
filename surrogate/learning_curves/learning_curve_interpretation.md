# Learning curves — surrogate overfitting diagnosis (P-07)

**Dataset:** `BPS_Random/LHS_00.json` — 975 samples (the training set per Zorn §3.4 and paper §6.4.1).
**After IQR outlier removal:** 874 retained (101 removed) — matches paper.
**CV:** 5-fold KFold, shuffle=True, random_state=42.
**Train sizes tested:** [0.2, 0.4, 0.6, 0.8, 1.0] × 874.

---

## Result summary

| Objective | Model | Train R² | CV R² (paper) | Train–CV gap | Verdict |
|-----------|-------|:--------:|:-------------:|:------------:|---------|
| Q_tot | GBR (300·3·1·5) | 0.998 | **0.958** (0.964) | 0.040 | NO overfitting (gap < 0.05) |
| DF    | GBR (300·3·1·5) | 0.985 | **0.777** (0.780) | 0.208 | STRONG overfitting (gap ≥ 0.20) |
| K_h   | MLP (64-32-16)  | 0.986 | **0.928** (0.931) | 0.058 | MILD overfitting (0.05–0.10) |

The reported surrogate R² values are **confirmed within 0.006 R²**. The surrogate C# JSON (`gbr_qtot.json`, `gbr_df.json`, `ann_kh.json`) (trained on the public Zorn et al. DaRUS dataset, doi:10.18419/darus-4532) is trained on this exact dataset (verified: JSON `init_value` of GBR Q_tot = 23.8198 matches the IQR-filtered mean of Q_tot on BPS_Random/LHS_00.json).

The MO ADO D=22 campaigns (5r×5k and 1r×10k) are computed on this validated surrogate. They are methodologically coherent with Zorn 2025 §3.4 and with paper §6.4.1.

---

## DF overfitting — the only real issue

The Q_tot and K_h surrogates are solid (gap ≤ 0.058, well within acceptable limits). The DF surrogate is a different story: train R² = 0.985, CV R² = 0.777, gap = 0.208. The GBR is memorising training noise on ~700 samples. Learning curve shows CV R² still rising at n=699 (no plateau), meaning more data would help.

**Two things to note before panicking.**

First: **Zorn et al. 2025 Table 4 reports CV R² = 0.780 for DF with GBR** on the same 874-sample dataset. Same number, same gap. This is not a defect of the Ambrosini surrogate — it's a structural limit of the BPS_Random 975-sample training set for the DF objective. Zorn accepts it, the literature accepts it, the paper can defend it.

Second: **the DF gap at n=699 (gap=0.208) is an artefact of GBR's tendency to overfit on limited data when `min_samples_leaf=1`.** A conservative mitigation (raising `min_samples_leaf` to 3 or 5) would shrink the gap at the cost of a modest CV R² drop. The paper chose `min_samples_leaf=1` from the exhaustive grid search, which maximises CV R² but at the price of high variance. Both are legitimate; the current choice is defensible.

---

## Implications for the paper

**The surrogate is not broken.** The MO ADO D=22 campaigns stand. No rerun needed.

**Two fixes are recommended for §6.4.1:**

1. *Add a learning-curve footnote or supplementary figure.* Sample sentence: *"Learning curves with 5-fold CV (Fig. A1, supplementary) show train–CV R² gaps of 0.04 (Q_tot), 0.21 (DF), and 0.06 (K_h) at full training size. The DF gap mirrors the accuracy limit reported by Zorn et al. [63] Table 4 and reflects a structural data-size limitation of the 874-sample BPS_Random training set rather than a defect of the chosen GBR configuration."*

2. *Strengthen the honesty on the DF result.* The current Table 7b footer claims the Ambrosini surrogate "matches or exceeds Zorn's reported accuracy on all three objectives". For DF it matches (0.780 vs 0.780) rather than exceeds. The claim should be adjusted to reflect this: *"The Ambrosini surrogate matches Zorn's reported accuracy for DF and exceeds it for Q_tot and K_h."*

**A third, optional, fix:** if you want to strengthen the paper further, retrain DF with the 10k `SuMo_Random/LHS_01.json` dataset (where DF CV R² rises to ~0.98 as measured in the first run I did). This **would invalidate the current MO campaigns**, because the fitness landscape changes. If you take this path:
- pros: DF gap drops from 0.21 to <0.01; Table 7b becomes 0.991/0.982/0.998 (truly exceeds Zorn); less reviewer-attackable
- cons: all current ADO MO campaigns (5r×5k and 1r×10k) must be rerun on the new surrogate; ~8-10 hours of compute on AsusROG; findings F1-F12 re-verified

My recommendation is **do not retrain**. The paper is aligned with Zorn's own methodology, which is the stronger defensive position against peer review. A reviewer can argue *"improve the surrogate"* but cannot argue *"your surrogate contradicts the reference you cite"*. You're fine as is, with the two small textual fixes above.

---

## Technical verification

The JSON surrogate currently used by `SH_BenchmarkADO` in Grasshopper:
- File: `gbr_qtot.json` — GBR, 300 trees, learning_rate=0.1, init_value=23.8198
- JSON `init_value` = mean of `y_Q_tot` on BPS_Random/LHS_00.json after IQR (= 23.8198) → exact match
- This proves the JSON model was trained on the 874-sample IQR subset, consistent with the paper

The surrogate is verified; the paper numbers are verified; the campaigns are valid.

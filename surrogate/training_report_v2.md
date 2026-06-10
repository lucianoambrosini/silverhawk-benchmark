# Surrogate Ambrosini v2 — Training Report

- Input dataset: `LHS_01.json` (10001 samples)
- After IQR (union per-obj): 9899 retained
- Features (n=22): ['row4_X', 'row5_X', 'wall_type', 'row2_Z', 'SH', 'max. ACH', 'row1_Y', 'natural_ventilation', 'activated_mass', 'row5_Y', 'ceiling_type', 'row3_X', 'row2_Y', 'row1_Z', 'row4_Y', 'Thickness', 'row3_Z', 'row4_Z', 'row3_Y', 'row1_X', 'row5_Z', 'row2_X']
- CV: 5-fold KFold (shuffle=True, random_state=42)
- GBR grid search: NO (using v1 winners)

## Accuracy summary

| Objective | Model | CV R² | Train R² | Gap | Paper v1 CV R² | Δ vs v1 |
|-----------|-------|:-----:|:--------:|:---:|:--------------:|:-------:|
| Q_tot | GBR | **0.9907** | 0.9939 | 0.0032 | 0.964 | +0.0267 |
| DF | GBR | **0.9825** | 0.9894 | 0.0069 | 0.780 | +0.2025 |
| K_h | MLP | **0.9961** | 0.9974 | 0.0013 | 0.931 | +0.0651 |

## GBR hyperparameters used

- **Q_tot**: {'n_estimators': 300, 'max_depth': 3, 'min_samples_leaf': 1, 'min_samples_split': 5}
- **DF**: {'n_estimators': 300, 'max_depth': 3, 'min_samples_leaf': 1, 'min_samples_split': 5}

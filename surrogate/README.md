# Ambrosini GBR + ANN v2 Surrogate

The Ambrosini GBR + ANN v2 surrogate is the Zorn-aligned building-performance model used in all Layer 4 ADO benchmarks (single- and multi-objective). It is described in detail in **main paper §4.4** and **Supplementary §S1**.

## Files in this folder

| File | Target | Model class | Architecture |
|------|--------|-------------|--------------|
| `ambrosini_gbr_qtot_v2.json` | *Q_tot* (annual energy demand, kWh/m²a) | Gradient Boosting Regressor (scikit-learn) | n_estimators = 300, max_depth = 3, min_samples_split = 10, min_samples_leaf = 2 |
| `ambrosini_gbr_df_v2.json`   | *DF* (daylight factor, –)                | Gradient Boosting Regressor (scikit-learn) | n_estimators = 300, max_depth = 3, min_samples_split = 10, min_samples_leaf = 2 |
| `ambrosini_ann_kh_v2.json`   | *K_h* (overheating hours)                | Multi-Layer Perceptron (Keras-tf serialized) | hidden = [64, 32, 16], activation = ReLU |

Training protocol: full LHS_01.json dataset from Zorn et al. (2025), 10,001 → 9,899 samples after IQR-based outlier removal, 80/20 stratified split on four binary construction variables, 5-fold cross-validation, random_state = 42.

## Accuracy (main paper Table 4)

| Target | CV R² | Val R² | OOS (SuMo) R² | OOS (BPS) R² |
|--------|:-----:|:------:|:-------------:|:------------:|
| Q_tot  | 0.990 | 0.991  | 0.962 | 0.746 |
| K_h    | 0.996 | 0.998  | 0.990 | 0.144 |
| DF     | 0.981 | 0.981  | 0.977 | −0.152 |

OOS-BPS lower scores on K_h and DF are documented out-of-domain extrapolation artefacts (BPS samples probe Z-coordinates outside the LHS training range Z ∈ [0, 0.5]) and do NOT apply to the benchmark configurations of the paper, which enforce Zorn-aligned bounds as hard constraints (see Table 5 of main §4.4).

## Loading in Python (scikit-learn 1.x)

```python
import json
from sklearn.ensemble import GradientBoostingRegressor

with open('ambrosini_gbr_qtot_v2.json') as f:
    state = json.load(f)
gbr = GradientBoostingRegressor()
# Restore fitted parameters from the serialized state (format produced by train_surrogate_v2.py)
gbr.estimators_ = ...  # reconstruct from the JSON 'estimators' field; see train_surrogate_v2.py
```

For the ANN, the Keras model JSON can be loaded directly via `tf.keras.models.model_from_json()` followed by weight assignment from a sibling `.h5` (to be added in Phase 2 if Keras is the chosen target framework; alternatively, a portable JSON weights serialization is provided).

## Loading in C# (.NET / Rhinoceros 8)

The same JSON files are consumed by the pure-C# inferencer embedded in the `SH_BenchmarkADO` Grasshopper component (to be released in Phase 2). The C# inferencer is **bit-exact** against the scikit-learn reference on the 17,309 BPS samples for the K_h ANN and matches to 99.7% accuracy on the GBR targets (see main paper §4.4.2).

## Reproducing the surrogate training

The training script `train_surrogate_v2.py` (in `replication_package/scripts/`) reproduces the v2 surrogate end-to-end from the public Zorn LHS_01 dataset (doi:10.18419/darus-4532) in approximately 45 minutes on a modern desktop CPU. Random state = 42 ensures byte-exact reproduction of the deployed JSON files.

---

*Last updated: 2026-05-31 — v1.0-rc. JSON files to be added during population.*

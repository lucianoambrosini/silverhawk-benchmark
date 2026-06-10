# Scripts

Python scripts that reproduce the Ambrosini GBR + ANN v2 surrogate and its training diagnostics
from the public Zorn et al. dataset. (Figure rendering is not scripted here — the per-figure
underlying numbers are provided directly in `../figures_source_data/`.)

## Files

| Script | Purpose | Input | Output |
|--------|---------|-------|--------|
| `train_surrogate_v2.py` | Reproduce the surrogate training end-to-end (GBR for Q_tot/DF, ANN for K_h; IQR cleaning, 80/20 split, 5-fold CV, `random_state = 42`) | Zorn LHS_01 dataset (doi:10.18419/darus-4532) | `../surrogate/ambrosini_*_v2.json` |
| `learning_curves.py` | Generate the surrogate learning curves and summary | training data + `../surrogate/*.json` | `../surrogate/learning_curves/*` |

## Requirements

```
python ≥ 3.10
numpy ≥ 1.25
scikit-learn ≥ 1.3
matplotlib ≥ 3.7        # learning curves
tensorflow ≥ 2.13 (Keras 3 compatible)   # K_h ANN — OR the portable JSON weights loader
```

## Usage

```bash
cd scripts
python train_surrogate_v2.py    # writes ../surrogate/ambrosini_*_v2.json (random_state=42 → byte-identical)
python learning_curves.py       # writes ../surrogate/learning_curves/
```

With `random_state = 42`, `train_surrogate_v2.py` reproduces the deployed surrogate JSON files
byte-for-byte.

## Phase 2 (post-publication)

Headless benchmark re-execution is provided separately by the pre-built **Falconry** console
(added at the SilverHawk Food4Rhino release; see `../falconry/`), together with the Grasshopper
definitions in `../grasshopper_assets/` for the canvas-side layers. No additional orchestration
script is shipped in Phase 1.

---

*Last updated: 2026-06. v1.0-rc.*

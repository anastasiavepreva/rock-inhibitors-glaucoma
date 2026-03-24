# Trained ocular property classifiers

| File | Property | Model type | Features | ROC-AUC |
|------|----------|------------|----------|---------|
| `corneal.pkl` | Corneal permeability | XGBClassifier | 43 RDKit physicochemical descriptors | 0.92 |
| `melanin.pkl` | Melanin binding | ExtraTreeClassifier | 167-bit MACCS fingerprints | 0.87 |
| `irritation.pkl` | Eye irritation | GradientBoostingClassifier | 167-bit MACCS fingerprints | 0.98 |

Loading:
- `corneal.pkl` and `melanin.pkl`: use `joblib.load()`
- `irritation.pkl`: use `pickle.load()`

Note: different generative methods may reference these models under slightly different filenames
(e.g. `corneal_tacogfn.pkl`, `irritation_rxnflow.pkl`). The `setup.sh` script symlinks
them into each method directory. The underlying models are identical.

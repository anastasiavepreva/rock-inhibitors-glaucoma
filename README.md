# Generative AI for Discovery of ROCK Inhibitors for Treatment of Glaucoma

Code and data accompanying the paper:

> **Generative AI for Discovery of ROCK Inhibitors for Treatment of Glaucoma**


## Repository structure

```
rock-inhibitors/
├── patches/                # Minimal diffs to upstream generative model repos
│   ├── rxnflow.patch
│   ├── tacogfn.patch
│   ├── evosbdd.patch
│   └── freedpp.patch
│   (DrugFlow requires no patch, only upstream repo + config)
├── models/                 # Trained ocular property classifiers (.pkl)
│   ├── corneal.pkl
│   ├── melanin.pkl
│   └── irritation.pkl
├── data/
│   ├── ocular/             # Training data for ocular property models
│   ├── receptor/           # ROCK-2 structure (PDB ID: 6ED6)
│   └── alert_collections.csv
├── configs/                # Run configurations for each method
├── scripts/
│   ├── setup.sh            # Clone upstream repos + apply patches
│   ├── train_ocular_models.py
│   └── run_generation.sh
├── notebooks/              # Analysis and figure reproduction
└── results/                # Generated molecules and evaluation outputs
```

## Quick start

### 1. Clone and set up

```bash
git clone https://github.com/<your-org>/rock-inhibitors.git
cd rock-inhibitors
bash scripts/setup.sh
```

`setup.sh` will clone each upstream repository at the pinned commit and apply the corresponding patch.

### 2. Install dependencies

Each generative method has its own environment. See the upstream READMEs linked below for installation instructions.

| Method | Upstream repository | Pinned commit |
|--------|-------------------|---------------|
| RxnFlow | [SeonghwanSeo/RxnFlow](https://github.com/SeonghwanSeo/RxnFlow) | `TODO` |
| TacoGFN | [tsa87/tacogfn](https://github.com/tsa87/tacogfn) | `TODO` |
| DrugFlow | [LPDI-EPFL/DrugFlow](https://github.com/LPDI-EPFL/DrugFlow) | `TODO` |
| EvoSBDD | (custom implementation) | -- |
| FREED++ | [AIRI-Institute/FFREED](https://github.com/AIRI-Institute/FFREED) | `TODO` |

### 3. Download pretrained models / data

```bash
# Ocular property classifiers are included in models/
# ROCK-2 receptor structure
wget -P data/receptor/ https://files.rcsb.org/download/6ED6.pdb
```

### 4. Run generation

See method-specific instructions in each section below.

## Generative methods

### RxnFlow

Modifications: added three ocular objectives (corneal permeability, melanin binding, irritation) to the multi-objective reward.

```bash
# Zero-shot generation
cd methods/rxnflow
python scripts/sampling_zeroshot.py \
  --model_path ./weights/qvina-unif-0-64_20250512.pt \
  --env_dir ./data/envs/zincfrag \
  -p 6ed6_rec.pdb \
  -c 26.909 47.024 52.508 \
  -o zeroshot_6ed6.csv \
  -n 256 \
  --subsampling_ratio 0.1 \
  --cuda

# Few-shot finetuning + generation
python scripts/few_shot_unidock_moo.py \
  --env_dir ./data/envs/zincfrag \
  --out_dir ./few_shot_6ed6 \
  --pretrained_model ./weights/qvina-unif-0-64_20250512.pt \
  -n 1000 \
  -p 6ed6_rec.pdb \
  -c 26.909 47.024 52.508 \
  -s 22.5 22.5 22.5 \
  --search_mode fast \
  --subsampling_ratio 0.04
```

### TacoGFN

Modifications: replaced PharmacoNet proxy with Uni-Dock for docking score computation; added three ocular objectives (corneal, melanin, irritation) multiplied into the reward.

Prerequisites: create pharmacophore and pocket databases for ROCK-2 using the provided notebooks (see TacoGFN upstream examples `2.2_compute_pharmacophores_for_alpha.ipynb` and `3_store_pharmacophores_pocket_lmdb.ipynb`). Ocular property models (`corneal.pkl`, `melanin.pkl`, `irritation.pkl`) and receptor (`6ed6_rec.pdbqt`) must be in the working directory.

```bash
cd methods/tacogfn

# Few-shot finetuning
python3 src/tacogfn/tasks/pharmaco_frag.py --hps_path hps/6ed6.json

# Generation
python3 src/tasks/generate_molecules.py \
  --model_path logs/6ed6/model_state_1000.pt \
  --save_folder fewshot_6ed6
```

### DrugFlow

DrugFlow is used without modification from the upstream repository. No patch is needed.

```bash
cd methods/drugflow

# Download checkpoint
wget -P checkpoints/ https://zenodo.org/records/14919171/files/drugflow_pa_comb.ckpt

# Generate molecules
python src/generate.py \
  --protein ../../data/receptor/6ed6_clean.pdb \
  --ref_ligand ../../data/receptor/6ed6_ligand.sdf \
  --checkpoint checkpoints/drugflow.ckpt \
  --molecule_size 15,30 \
  --output samples_6ed6.sdf \
  --pocket_distance_cutoff 12 \
  --n_samples 256 \
  --metrics_output metrics_6ed6.csv \
  --gnina $CONDA_PREFIX/bin/gnina
```

### EvoSBDD

*Instructions will be added when code is provided.*

### FREED++

Modifications: added three ocular objectives to the weighted-sum reward.

```bash
cd methods/freedpp
python main.py \
  --exp_root ../experiments \
  --alert_collections ../../data/alert_collections.csv \
  --fragments ../../data/zinc_crem.json \
  --receptor ../../data/receptor/6ed6.pdbqt \
  --vina_program ./env/qvina02 \
  --starting_smile "n1c(*)c(*)c(*)c2c(*)c(*)c(*)c(*)c12" \
  --fragmentation crem \
  --num_sub_proc 12 \
  --n_conf 1 \
  --exhaustiveness 1 \
  --save_freq 10 \
  --epochs 200 \
  --reward_version soft \
  --box_center "16.309 37.516 18.544" \
  --box_size "10,10,10" \
  --seed 100 \
  --objectives "DockingScore,Corneal,Melanin,Irritation" \
  --weights "1.0,1.0,1.0,1.0"
```

## Scoring and re-ranking

Generated candidates were scored using a multi-fidelity pipeline:

1. **QVina docking** (during generation, as part of the reward)
2. **Boltz-2 re-ranking** (independent structural evaluation)
3. **FEP calculations** (final validation of top hits via YANK/OpenMM)

## Citation



## License

TODO

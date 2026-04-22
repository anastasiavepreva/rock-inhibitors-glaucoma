# BADGER DecompDiff 6ED6 Generation Bundle

This bundle contains only the files needed to generate `6ed6` samples with the current DecompDiff single-protein script:

- `scripts/sample_one_protein.py`
- `configs/sampling_drift_guided.yml`
- `configs/sampling_drift_unguided.yml`
- `configs/arm_num_config.pkl`
- `configs/scaffold_num_config.pkl`
- `checkpoints/pretrained_models/uni_o2_bond.pt`
- `checkpoints/load_ckpt/decompdiff_single_constraints/ckpt.pt`
- `pockets/6ed6_clean_pocket_15.pdb`

## What To Install

Clone BADGER and use the DecompDiff branch:

```bash
git clone https://github.com/ASK-Berkeley/BADGER-SBDD.git
cd BADGER-SBDD
git checkout decompdiff
```

Install the BADGER environment. The upstream README recommends Ubuntu 24 and either:

1. `conda env create -f BADGER.yml`
2. Or manual installation:

```bash
conda create -n badger_env python=3.12
conda activate badger_env
pip install torch
pip install torch_geometric
pip install pyg_lib torch_scatter torch_sparse torch_cluster torch_spline_conv -f https://data.pyg.org/whl/torch-2.7.0+cu126.html
conda install rdkit openbabel tensorboard pyyaml easydict python-lmdb -c conda-forge
pip install meeko==0.1.dev3 scipy pdb2pqr vina==1.2.2
python -m pip install git+https://github.com/Valdes-Tresanco-MS/AutoDockTools_py3
```

## How To Use This Bundle

Unzip this bundle into the BADGER repository root so the files land under `scripts/`, `configs/`, `checkpoints/`, and `pockets/`.

The included pocket file already corresponds to the `6ed6` pocket with box size `15 x 15 x 15`, so the box dimensions are informational only. The single-protein script consumes the pocket PDB directly.

Use this pocket center:

```text
16.309 37.516 18.544
```

## Guided Generation

```bash
python scripts/sample_one_protein.py configs/sampling_drift_guided.yml   --pdb pockets/6ed6_clean_pocket_15.pdb   --center 16.309 37.516 18.544   --prior_mode subpocket   --outdir results/ligands   --outfile decompdiff_guided_6ed6_samples.pt   --num 256   --device cuda:0
```

This config uses:

- classifier guidance scale: `100`
- context delta: `-40`
- clip: `1e-3`
- diffusion checkpoint: `checkpoints/pretrained_models/uni_o2_bond.pt`
- classifier checkpoint: `checkpoints/load_ckpt/decompdiff_single_constraints/ckpt.pt`

## Unguided Generation

```bash
python scripts/sample_one_protein.py configs/sampling_drift_unguided.yml   --pdb pockets/6ed6_clean_pocket_15.pdb   --center 16.309 37.516 18.544   --prior_mode subpocket   --outdir results/ligands   --outfile decompdiff_unguided_6ed6_samples.pt   --num 256   --device cuda:0
```

This config is identical except `scale_factor = 0`.

## Required Checkpoints Only

Only the two checkpoints required by `scripts/sample_one_protein.py` are included:

- diffusion model: `checkpoints/pretrained_models/uni_o2_bond.pt`
- classifier: `checkpoints/load_ckpt/decompdiff_single_constraints/ckpt.pt`

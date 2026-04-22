# BADGER TargetDiff 6ED6 Generation Bundle

This bundle contains only the files needed to generate `6ed6` samples with the TargetDiff single-protein script:

- `scripts/sample_one_protein.py`
- `configs/sampling_guided.yml`
- `configs/sampling_unguided.yml`
- `checkpoints/pretrained_models/pretrained_diffusion.pt`
- `checkpoints/load_ckpt/targetdiff_single_constraint_egnn/ckpt.pt`
- `pockets/6ed6_clean_pocket_15.pdb`

## What To Install

Clone BADGER and use the `main` branch:

```bash
git clone https://github.com/ASK-Berkeley/BADGER-SBDD.git
cd BADGER-SBDD
git checkout main
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

This guided config uses the values we agreed to keep for TargetDiff:

- guidance strength `s = 30`
- atom-type guidance `s_v = 0`
- context `-16`
- clip `3e-3`
- `num_samples = 256`

```bash
python scripts/sample_one_protein.py   --config configs/sampling_guided.yml   --pdb pockets/6ed6_clean_pocket_15.pdb   --center 16.309 37.516 18.544   --outfile results/ligands/targetdiff_guided_6ed6_samples.pt   --device cuda:0
```

## Unguided Generation

This config keeps the same context and clip but disables guidance with `s = 0`.

```bash
python scripts/sample_one_protein.py   --config configs/sampling_unguided.yml   --pdb pockets/6ed6_clean_pocket_15.pdb   --center 16.309 37.516 18.544   --outfile results/ligands/targetdiff_unguided_6ed6_samples.pt   --device cuda:0
```

## Downloading Checkpoints

Checkpoints are hosted on Zenodo. They will be downloaded automatically by `setup.sh`, or manually:

```bash
mkdir -p checkpoints/pretrained_models
mkdir -p checkpoints/load_ckpt/targetdiff_single_constraint_egnn
wget -O checkpoints/pretrained_models/pretrained_diffusion.pt "https://zenodo.org/records/19701457/files/pretrained_diffusion.pt?download=1"
wget -O checkpoints/load_ckpt/targetdiff_single_constraint_egnn/ckpt.pt "https://zenodo.org/records/19701457/files/ckpt.pt?download=1"
```

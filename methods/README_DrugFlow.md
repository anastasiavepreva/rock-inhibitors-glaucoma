# DrugFlow

## Setup

```bash

git clone https://github.com/LPDI-EPFL/DrugFlow.git
cd DrugFlow

```

### Conda Environment

Create a conda/mamba environment 
```bash
conda env create -f environment.yaml -n drugflow
conda activate drugflow
```

and add the Gnina executable for docking score computation
```bash
wget https://github.com/gnina/gnina/releases/download/v1.1/gnina -O $CONDA_PREFIX/bin/gnina
chmod +x $CONDA_PREFIX/bin/gnina
```

# Sampling

```bash
# Download a model
wget -P checkpoints/ https://zenodo.org/records/14919171/files/drugflow_pa_comb.ckpt

python src/generate.py \\n  --protein examples/6ed6_clean.pdb \\n  --ref_ligand examples/6ed6_ligand.sdf \\n  --checkpoint checkpoints/drugflow.ckpt --molecule_size 15,30\\n  --output examples/samples_6ed6.sdf --pocket_distance_cutoff 12 --n_samples 256 --metrics_output metrics_6ed6.csv --gnina $CONDA_PREFIX/bin/gnina
```


# Aligning Target-Aware Molecule Diffusion Models with Exact Energy Optimization


> [**Aligning Target-Aware Molecule Diffusion Models with Exact Energy Optimization**](https://arxiv.org/abs/2407.01648)


## Environment
```bash
conda create -n target python=3.8
conda activate target
conda install pytorch==2.0.1 pytorch-cuda=11.7 -c pytorch -c nvidia
conda install pyg -c pyg
pip install pyg_lib torch_scatter torch_sparse torch_cluster torch_spline_conv -f https://data.pyg.org/whl/torch-2.0.0+cu117.html
conda install rdkit openbabel tensorboard pyyaml easydict python-lmdb -c conda-forge

# For Vina Docking
pip install meeko==0.1.dev3 scipy pdb2pqr vina==1.2.2 
python -m pip install git+https://github.com/Valdes-Tresanco-MS/AutoDockTools_py3
```

-----

## Repo clone
```bash 
git clone https://github.com/MinkaiXu/AliDiff.git
```

## Training (Optional)

### Data Generation

#### SFT Data
The data preparation follows (https://github.com/guanjq/targetdiff).

#### Preference Data
```bash
python gen_data.py
```

### Train
Move ipnet2 and training_ipo.yml config to the pretrained_models and configs folders.

```bash
python scripts/train_ipo.py configs/training_ipo.yml
```

### Sample for 6ed6 pocket 
Move sampling.yml config to configs folder.

```bash
python sample_one_protein.py configs/sampling.yml --pdb pockets/6ed6_clean_pocket_12.pdb --center 26.9098 47.024 52.50861
```

# ROCK-2 receptor structure

Download from the Protein Data Bank:

```bash
wget https://files.rcsb.org/download/6ED6.pdb
```

PDB ID: 6ED6 (high-resolution crystal structure of ROCK-2).

For docking with QVina/AutoDock Vina, convert to PDBQT format:

```bash
# Using ADFR suite
prepare_receptor -r 6ED6.pdb -o 6ed6.pdbqt
```


import os
from typing import List

from rdkit.Chem.rdchem import Mol as RDMol
import numpy as np
import torch

from mflow.models.hyperparams import Hyperparameters
from mflow.utils.model_utils import load_model, get_latent_vec
from mflow.models.utils import (
    check_validity, adj_to_smiles, check_novelty, valid_mol,
    construct_mol, _to_numpy_array, correct_mol,valid_mol_can_with_seg
)


class MoFlowDecoder:
    def __init__(self, model_dir, device):
        snapshot_path = "model_snapshot_epoch_200"
        hyperparams_path = "moflow-params.json"

        snapshot_path = os.path.join(model_dir, snapshot_path)
        hyperparams_path = os.path.join(model_dir, hyperparams_path)

        model_params = Hyperparameters(path=hyperparams_path)
        model = load_model(snapshot_path, model_params, debug=True)
        model.to(device)
        model.eval()  # Set model for evaluation

        self.atomic_num_list = [6, 7, 8, 9, 15, 16, 17, 35, 53, 0]

        self.decoder = model

        self.correct_validity = True
        self.largest_connected_comp = True

        self.z_dim = model.b_size + model.a_size
        self.device = device

    def reconstruct(self, adj: np.ndarray, x: np.ndarray) -> List[RDMol]:
        adj = _to_numpy_array(adj)  # , gpu)  (1000,4,9,9)
        x = _to_numpy_array(x)  # , gpu)  (1000,9,5)
        if self.correct_validity:
            # valid = [valid_mol_can_with_seg(construct_mol_with_validation(x_elem, adj_elem, atomic_num_list)) # valid_mol_can_with_seg
            #          for x_elem, adj_elem in zip(x, adj)]
            valid = []
            for x_elem, adj_elem in zip(x, adj):
                mol = construct_mol(x_elem, adj_elem, self.atomic_num_list)
                # Chem.Kekulize(mol, clearAromaticFlags=True)
                cmol = correct_mol(mol)
                vcmol = valid_mol_can_with_seg(cmol, largest_connected_comp=self.largest_connected_comp)   #  valid_mol_can_with_seg(cmol)  # valid_mol(cmol)  # valid_mol_can_with_seg
                # Chem.Kekulize(vcmol, clearAromaticFlags=True)
                valid.append(vcmol)
        else:
            valid = [valid_mol(construct_mol(x_elem, adj_elem, self.atomic_num_list))
                for x_elem, adj_elem in zip(x, adj)]   #len()=1000
        return valid

    @torch.no_grad()
    def __call__(self, z: np.ndarray) -> List[RDMol]:
        assert isinstance(z, np.ndarray) and (z.ndim == 2) and (z.shape[1] == self.z_dim)
        z = torch.tensor(z, device=self.device, dtype=torch.float32)
        adj, x = self.decoder.reverse(z)
        # # val_res = check_validity(adj, x, atomic_num_list, correct_validity=args.correct_validity)
        mols = self.reconstruct(adj, x)
        return mols

import abc
import argparse
import os
from pathlib import Path
import pickle
from typing import Callable, Dict, List, Optional, Tuple, Union
import tempfile
import json
import joblib
from dataclasses import dataclass
import itertools

from sklearn.base import ClassifierMixin
from rdkit import Chem
from rdkit.Chem.rdchem import Mol as RDMol
from rdkit.Chem import MACCSkeys, rdMolDescriptors

import numpy as np
import torch
import cma

from .moflow import MoFlowDecoder
from .unidock import run_unidock, Box

rdMolDescriptorsPropertiesNames = list(rdMolDescriptors.Properties.GetAvailableProperties())
rdMolDescriptorsProperties = rdMolDescriptors.Properties(rdMolDescriptorsPropertiesNames)
DEVICE = torch.device('cuda')


def truncated_maccs_descriptor(molecule: RDMol) -> np.ndarray:
    descriptor = MACCSkeys.GenMACCSKeys(molecule)
    descriptor = [int(bit) for bit in descriptor.ToBitString()[:167]]
    descriptor = np.array(descriptor)
    return descriptor


def rdkit_descriptor(molecule: RDMol) -> np.ndarray:
    descriptor = rdMolDescriptorsProperties.ComputeProperties(molecule)
    descriptor = np.array(descriptor)
    return descriptor


def batched_call(
    func: Callable,
    x: List,
    batch_size: int = 1,
):
    x = itertools.batched(x, batch_size)
    y = [func(x) for x in x]
    y = itertools.chain(*y)
    return y


class BatchedMolObjective:
    "Simple abstract class for computing batched objective on unique molecules from the batch using cache."
    def __init__(
        self,
        error_value: float = 0,
        cache: Dict = None,
        batch_size: int = 32,
    ):
        self.error_value = error_value
        if cache is None:
            cache = dict()
        self.cache = cache
        self.batch_size = batch_size
        self.history = []

    def __call__(self, mols: List[RDMol]) -> List[float]:
        smis = [Chem.MolToSmiles(mol) if mol is not None else "None" for mol in mols]
        self.history += smis
        scores = [self.error_value] * len(mols)
        valid_ids = [i for i, mol in enumerate(mols) if mol is not None]
        valid_mols = [mol for mol in mols if mol is not None]
        valid_smis = [Chem.MolToSmiles(mol) for mol in valid_mols]
        novel_uniq_smis = list(set(valid_smis).difference(self.cache))
        novel_uniq_mols = [Chem.MolFromSmiles(smi) for smi in novel_uniq_smis]
        novel_scores = batched_call(self.objective, novel_uniq_mols, self.batch_size)
        novel_cache = dict(zip(novel_uniq_smis, novel_scores))
        self.cache.update(novel_cache)
        for idx, smi in zip(valid_ids, valid_smis):
            scores[idx] = self.cache[smi]
        return scores

    @abc.abstractmethod
    def objective(self, mols: List[RDMol]) -> List[float]:
        pass


class DescriptorClassifierBatchedMolObjective(BatchedMolObjective):
    def __init__(
        self,
        model: ClassifierMixin,
        error_value: float = 0,
        cache: Dict = None,
        batch_size: int = 32,
    ):
        super().__init__(
            error_value=error_value,
            cache=cache,
            batch_size=batch_size,
        )
        self.model = model

    def objective(self, mols: List[RDMol]) -> List[float]:
        if len(mols) == 0:
            return []
        X = [self.descriptor(mol) for mol in mols]
        X = np.array(X)
        scores = self.model.predict_proba(X)[:, 1]
        scores = scores.tolist()
        if hasattr(self, "_postprocess"):
            scores = [self._postprocess(score) for score in scores]
        return scores


class IrritationScore(DescriptorClassifierBatchedMolObjective):
    descriptor = truncated_maccs_descriptor

    def _postprocess(self, score):
        return 1 - score


class MelaninScore(DescriptorClassifierBatchedMolObjective):
    descriptor = truncated_maccs_descriptor


class CornealScore(DescriptorClassifierBatchedMolObjective):
    descriptor = rdkit_descriptor


class LatentBatchedMultiObjective:
    def __init__(self, decoder: Callable, **objectives: Dict[str, BatchedMolObjective]):
        self.decoder = decoder
        assert all(isinstance(objective, BatchedMolObjective) for objective in objectives.values())
        self.objectives = objectives

    # def __call__(self, z: np.ndarray | List[np.ndarray]) -> List[float]:
    def __call__(self, z: np.ndarray) -> List[float]:
        if isinstance(z, np.ndarray):
            assert z.ndim == 2
            assert z.shape[1] == self.z_dim
        elif isinstance(z, list):
            assert all(isinstance(i, np.ndarray) for i in z)
            assert all(i.ndim == 1 for i in z)
            assert all(len(i) == self.decoder.z_dim for i in z)
            z = np.array(z)
        else:
            raise TypeError(type(z))
        mols = self.decoder(z)
        scores = [objective(mols) for _, objective in self.objectives.items()]
        return np.array(scores).prod(axis=0).tolist()


@dataclass
class DockingConfig:
    receptor: str | Path
    center_x: float
    center_y: float
    center_z: float
    size_x: float = 22.5
    size_y: float = 22.5
    size_z: float = 22.5


class DockingScore(BatchedMolObjective):
    def __init__(
        self,
        config: DockingConfig,
        error_value: float = 0,
        cache: Dict = None,
        batch_size: int = 32,
    ):
        super().__init__(
            error_value=error_value,
            cache=cache,
            batch_size=batch_size,
        )
        self.config = config
        self.docking_box = Box(
            center_x=config.box_center_x,
            center_y=config.box_center_y,
            center_z=config.box_center_z,
            size_x=config.box_size_x,
            size_y=config.box_size_y,
            size_z=config.box_size_z,
        )
        self.receptor = Path(self.config.receptor)
        assert self.receptor.exists()

    def objective(self, mols: List[RDMol]) -> List[float]:
        if len(mols) == 0:
            return []
        with tempfile.TemporaryDirectory() as workdir:
            docked_mols = run_unidock(
                receptor=self.receptor,
                ligands=mols,
                box=self.docking_box,
                workdir=workdir,
                num_modes=1,
                search_mode="fast",
                seed=42,
            )
            docking_scores = [float(mol.GetProp("docking_score")) if mol else self.error_value for mol in docked_mols]
        return docking_scores


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--save_dir', type=str, default='./')
    parser.add_argument('--sigma', type=float, default=1)
    parser.add_argument('--sigma0', type=float, default=0.25)
    parser.add_argument('--popsize', type=int, default=64)
    parser.add_argument('--maxiter', type=int, default=10)
    parser.add_argument('--restarts', type=int, default=99)

    parser.add_argument('--receptor', type=str, required=True)
    parser.add_argument('--center_x', type=float, required=True)
    parser.add_argument('--center_y', type=float, required=True)
    parser.add_argument('--center_z', type=float, required=True)

    parser.add_argument('--corneal_model', type=str, required=True)
    parser.add_argument('--melanin_model', type=str, required=True)
    parser.add_argument('--irritation', type=str, required=True)
    parser.add_argument('--moflow_model', type=str, required=True)

    args = parser.parse_args()

    decoder = MoFlowDecoder()

    docking_config = DockingConfig(
        receptor=args.receptor,
        center_x=args.center_x,
        center_y=args.center_y,
        center_z=args.center_z,
    )
    docking_objective = DockingScore(
        docking_config,
        batch_size=args.popsize,
    )
    corneal_model = joblib.load(args.corneal_model)
    corneal_objective = CornealScore(
        corneal_model,
        batch_size=args.popsize,
    )
    melanin_model = joblib.load(args.melanin_model)
    melanin_objective = MelaninScore(
        melanin_model,
        batch_size=args.popsize,
    )
    with open(args.irritation_model, 'rb') as f:
        irritation_model = pickle.load(f)
    irritation_objective = IrritationScore(
        irritation_model,
        batch_size=args.popsize,
    )

    objectives = {
        "DS": docking_objective,
        "IRR": irritation_objective,
        "MEL": melanin_objective,
        "COR": corneal_objective,
    }

    parallel_objective = LatentBatchedMultiObjective(
        decoder=decoder,
        **objectives,
    )

    sigma = args.sigma
    z_dim = decoder.z_dim

    def x0():
        z = np.random.randn(z_dim)
        return sigma * z

    options = cma.CMAOptions()
    options["popsize"] = args.popsize
    options['maxiter'] = args.maxiter

    res = cma.fmin(
        objective_function=None,
        x0=x0,
        sigma0=args.sigma0,
        options=options,
        args=(),
        gradf=None,
        restarts=args.restarts,
        restart_from_best=False,
        incpopsize=1,
        eval_initial_x=False,
        parallel_objective=parallel_objective,
        noise_handler=None,
        noise_change_sigma_exponent=1,
        noise_kappa_exponent=0,
        bipop=False,
        callback=None,
        init_callback=None,
    )

    os.makedirs(args.save_dir, exists_ok=True)
    cache = {name: objective.cache for name, objective in parallel_objective.objectives.items()}
    with open(os.path.join(args.save_dir, "cache.json"), "wt") as f:
        json.dump(cache, f)

    history = parallel_objective.objectives["docking"].history
    with open(os.path.join(args.save_dir, "history.json"), "wt") as f:
        json.dump(history, f)

    del res[-2].objective_function
    del res[-2].parallel_objective
    with open(os.path.join(args.save_dir, "res.pkl"), "wb") as f:
        pickle.dump(res, f)

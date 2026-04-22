import traceback
from typing import List, Dict, Optional
import pathlib
from dataclasses import dataclass

from rdkit import Chem
from rdkit.Chem.rdchem import Mol as RDMol
from rdkit.Chem.rdDistGeom import EmbedMolecule, srETKDGv3
from unidock_tools.application.unidock_pipeline import UniDock


def add_conformer(
    mol: RDMol,
    remove_hs: bool = True,
    timeout: int = 1,
    seed: int = 1,
) -> RDMol:
    mol = Chem.AddHs(mol)
    options = srETKDGv3()
    options.randomSeed = seed
    options.timeout = timeout  # prevent stucking
    EmbedMolecule(mol, options)
    if mol.GetNumConformers() == 0:
        raise RuntimeError("Failed to generate conformer.")
    if remove_hs:
        mol = Chem.RemoveHs(mol)
    return mol


@dataclass
class Box:
    center_x: float
    center_y: float
    center_z: float
    size_x: float = 22.5
    size_y: float = 22.5
    size_z: float = 22.5


def run_unidock(
    receptor: pathlib.Path,
    ligands: List[RDMol],
    box: Box,
    workdir: pathlib.Path,
    verbose: Optional[bool] = False,
    **kwargs: Dict,
) -> List[RDMol | None]:

    input_dir = workdir.joinpath("input")
    output_dir = workdir.joinpath("output")
    work_dir = workdir.joinpath("workdir")

    input_dir.mkdir(parents=True)
    output_dir.mkdir(parents=True)
    work_dir.mkdir(parents=True)

    ligand_files = []
    ligand_names = [f"{i}" for i, _ in enumerate(ligands)]
    for ligand, ligand_name in zip(ligands, ligand_names):
        if ligand.GetNumConformers() == 0:
            try:
                ligand = add_conformer(ligand)
            except RuntimeError:
                if verbose:
                    print(traceback.format_exc())
                continue
            except:
                if verbose:
                    print(traceback.format_exc())
                continue
        ligand_file = input_dir.joinpath(f"{ligand_name}.sdf")
        with Chem.SDWriter(str(ligand_file)) as writer:
            writer.write(ligand)
        ligand_files += [ligand_file]

    if len(ligand_files) > 0:
        runner = UniDock(
            receptor=receptor,
            ligands=ligand_files,
            center_x=box.center_x,
            center_y=box.center_y,
            center_z=box.center_z,
            size_x=box.size_x,
            size_y=box.size_y,
            size_z=box.size_z,
            workdir=work_dir,
        )
        runner.docking(
            save_dir=output_dir,
            **kwargs,
        )

    docked_ligands = []
    for ligand_name in ligand_names:
        docked_ligand_file = output_dir.joinpath(f"{ligand_name}.sdf")
        if docked_ligand_file.exists():
            docked_ligand = Chem.SDMolSupplier(
                docked_ligand_file,
                removeHs=False,
                sanitize=True
            )[0]
        else:
            docked_ligand = None
        docked_ligands += [docked_ligand]

    return docked_ligands

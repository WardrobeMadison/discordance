from typing import Dict, List

import h5py


def add_attributes(filename: str, searchon: List, paramname: str, attrs: Dict) -> None:
    """Adding attribute to epochs in h5 file

    Args:
            filename (str): Path to h5py file
            attr (pd.DataFrame): Indexed on params
    """
    f = h5py.File(filename, "a")
    experiment = f["experiment"]
    for epoch in experiment:
        key = "_".join(map(str,
                           [epoch.attrs[search]
                            for search in searchon]))
        epoch.attrs[paramname] = attrs.get(key)
    f.close()


def add_genotype(filename, genotype):
    f = h5py.File(filename, "a")
    experiment = f["experiment"]
    for epoch in experiment:
        f[f"experiment/{epoch}"].attrs["genotype"] = genotype
    f.close()

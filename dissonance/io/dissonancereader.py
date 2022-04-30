import multiprocessing as mp
import re
from functools import partial
from pathlib import Path
from typing import Dict, List

import h5py
import pandas as pd

RE_DATE = re.compile(r"^.*(\d{4}-\d{2}-\d{2})(\w\d?).*$")


class DissonanceReader:

    def __init__(self, paths: List[Path]):
        self.experimentpaths = []
        for path in paths:
            if path.is_dir():
                self.experimentpaths.extend(path.glob("*.h5"))
            else:
                self.experimentpaths.append(path)

    @staticmethod
    def file_to_paramstable(filepath: Path, paramnames: List[str], filters: Dict = None):
        try:
            matches = RE_DATE.match(str(filepath))
            prefix = matches[1].replace("-", "") + matches[2]

            data = []
            h5file = h5py.File(str(filepath), "a")
            experiment = h5file["experiment"]
            for epochname in experiment:
                epoch = experiment[epochname]

                condition = all(
                    [epoch.attrs.get(key) == val for key, val in filters.items()])
                if condition:
                    number = f"{int(epochname[5:]):04d}"

                    params = {key: epoch.attrs.get(key) for key in paramnames}
                    params["number"] = number
                    params["tracetype"] = epoch.attrs["tracetype"]
                    data.append(params)

            if len(data) > 0:
                df = pd.DataFrame.from_dict(data)
                df["startdate"] = pd.to_datetime(df["startdate"])
                df["exppath"] = filepath
                print(f"{filepath}: {df.shape[0]}")
                return df
            else:
                return None
        except Exception as e:
            print(filepath)
            print(e)
            return None

    def to_epochs(self, **kwargs) -> List:
        traces = []
        for ii, filepath in enumerate(self.experimentpaths):
            print(f"Loading {ii+1} / {len(self.experimentpaths)}: {filepath}")
            traces.extend(self.h5_to_epochs(filepath, **kwargs))
        return traces

    def to_params(self, paramnames: List[str], filters: Dict, nprocesses: int = 5) -> pd.DataFrame:
        dfs = []
        func = partial(self.file_to_paramstable,
                       paramnames=paramnames, filters=filters)

        if nprocesses == 1:
            for experimentpath in self.experimentpaths:
                df = func(experimentpath)
                dfs.append(df)
        else:
            with mp.Pool(processes=nprocesses) as p:
                for df in p.map(func, self.experimentpaths):
                    dfs.append(df)

        return pd.concat(dfs)


class DissonanceUpdater:
    RE_DATE = re.compile(r"^.*(\d{4}-\d{2}-\d{2})(\w\d?).*$")

    def __init__(self, disfilepath: Path):
        self.filepath = disfilepath

    def update_cell_labels(self):
        f = h5py.File(str(self.filepath), "r+")
        matches = self.RE_DATE.match(str(self.filepath))

        prefix = matches[1].replace("-", "") + matches[2]
        for epochgrp in f["experiment"]:
            epoch = f[f"experiment/{epochgrp}"]
            epoch.attrs["cellname"] = f'{prefix}_{epoch.attrs["cellname"].split("_")[-1]}'

    def undo_update_cell_labels(self):
        f = h5py.File(self.filepath, "r+")

        for name in f["experiment"]:
            epoch = f[f"experiment/{name}"]
            cellname = epoch.attrs["cellname"]
            epoch.attrs["cellname"] = cellname.split("_")[0]

        f.close()

    def add_attribute(self, paramname: str, paramval: object, filters: Dict) -> None:
        """Adding attribute to epochs in h5 file

        Args:
                filename (str): Path to h5py file
                attr (pd.DataFrame): Indexed on params
        """
        f = h5py.File(self.filepath, "r+")

        for name in f["experiment"]:
            epoch = f[f"experiment/{name}"]
            if all([
                    epoch.attrs[key] == val
                    for key, val in filters.items()]):
                epoch.attrs[paramname] = paramval

        f.close()

    def add_genotype(self, genotype):
        f = h5py.File(self.filepath, "r+")

        for name in f["experiment"]:

            epoch = f[f"experiment/{name}"]
            del epoch.attrs["genotype"]
            epoch.attrs["genotype"] = genotype

        f.close()

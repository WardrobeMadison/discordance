import multiprocessing as mp
import re
from functools import partial
from pathlib import Path
from typing import Dict, List

import h5py
import pandas as pd

from .. import epochtypes as et

RE_DATE = re.compile(r"^.*(\d{4}-\d{2}-\d{2})(\w\d?).*$")


class DissonanceReader:

    def __init__(self, filepaths: List[Path]):
        self.experimentpaths = filepaths

    @staticmethod
    def file_to_paramstable(filepath: Path, paramnames: List[str], filters: Dict = None):
        try:
            matches = RE_DATE.match(str(filepath))
            prefix = matches[1].replace("-", "") + matches[2]

            data = []
            h5file = h5py.File(str(filepath), "a")
            experiment = h5file["experiment"]
            for ii, epochname in enumerate(experiment):
                epoch = experiment[epochname]

                condition = all(
                    [epoch.attrs[key] == val for key, val in filters.items()])
                if condition:
                    number = f"{ii+1:04d}"

                    params = {key: epoch.attrs[key] for key in paramnames}
                    params["number"] = number
                    params["tracetype"] = epoch.attrs["tracetype"]
                    data.append(params)

            if len(data)>0:
                df =  pd.DataFrame.from_dict(data)
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
        func = partial(self.file_to_paramstable, paramnames=paramnames, filters=filters)

        if nprocesses == 1:
            for experimentpath in self.experimentpaths:
                df = func(experimentpath)
                dfs.append(df)
        else:
            with mp.Pool(processes=nprocesses) as p:
                for df in p.map(func, self.experimentpaths):
                    dfs.append(df)
        
        return pd.concat(dfs)

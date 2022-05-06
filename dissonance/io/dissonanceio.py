import multiprocessing as mp
import operator
import re
from functools import partial, reduce
from pathlib import Path
from typing import Any, Dict, List, Tuple, Union

import h5py
import pandas as pd

from ..analysis.analysistree import AnalysisTree
from ..epochtypes import epoch_factory

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
            #prefix = matches[1].replace("-", "") + matches[2]

            data = []
            h5file = h5py.File(str(filepath), "a")
            experiment = h5file["experiment"]
            for epochname in experiment:
                epoch = experiment[epochname]

                if filters is not None:
                    condition = all(
                        [epoch.attrs.get(key) == val for key, val in filters.items()])
                else:
                    condition = True
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

    def to_params(self, paramnames: List[str], filters: Dict = None, nprocesses: int = 5) -> pd.DataFrame:
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


class EpochIO:

    def __init__(self, params: pd.DataFrame, experimentpaths: List[Path], unchecked: set = None):
        self.files = {
            path: h5py.File(str(path), "a")["experiment"] for path in experimentpaths
        }
        # GROUP EPOCHS INTO FLAT LIST
        self.unchecked = set() if unchecked is None else unchecked
        self.set_frame(params)

    def to_tree(self, name, splits) -> AnalysisTree:
        return AnalysisTree(name, splits, self.frame)

    def set_frame(self, params: pd.DataFrame):
        params.loc[:, "include"] = params.startdate.apply(
            lambda x: not (x in self.unchecked))
        self.frame = params

    def update(self, filters: List[Dict], paramname: str, value: Any):
        # FILTER DATATABLE TO APPLICABLE EPOCHS
        eframe = self.query(filters=filters)

        for _, row in eframe.iterrows():
            # UPDATE H5 GROUP ATTRIBUTES
            row["epoch"].update(paramname, value)
            # UPDATE EPOCHIO DATATABLE PARAMETERS
            if paramname in self.frame.columns:
                self.frame.loc[self.frame.startdate ==
                               row["startdate"], paramname] = value

        # FLUSH CHANGES MADE TO ANY H5 FILES
        for experimentgrp in self.files.values():
            experimentgrp.file.flush()

    def query(self, filters=List[Dict], useincludeflag=True) -> pd.DataFrame:
        """Relate nodes from tree to underlying dataframe. Only passes inclued nodes

        Args:
                node (Node): Node's path used for lookup

        Returns:
                Union[Traces, ITrace]: Traces or individual Trace for leaf node
        """
        if not isinstance(filters, list):
            filters = [filters]

        dfs = []
        for filter in filters:
            if "Name" in filter.keys():
                del filter["Name"]
            if len(filter) == 1 and list(filter.keys())[0] == "startdate":
                dfs.append(self.frame.query(
                    f"startdate == '{filter['startdate']}'"))
            else:
                # DICTIONARY OF ALL VALUES
                # BUILD FILTER CONDITION
                # FILTERED ON INDEX SO ONLY NEED VALUES IN LABEL ORDER
                condition = []
                for key, value in filter.items():
                    if value is None:
                        condition.append(
                            self.frame[key].apply(lambda x: x is None)
                        )
                    else:
                        condition.append(
                            self.frame[key] == value
                        )
                dff = self.frame.loc[reduce(operator.and_, condition), :]

                # FILTER FOR CHECKED VALUES
                if useincludeflag is False:
                    dfs.append(dff)
                else:
                    dfs.append(dff.loc[dff.include == True])
        # CONVERT TO EPOCHS IN DATAFRAME
        if len(dfs) == 0:
            raise Exception("No epochs returns")
        else:
            df = (pd.concat(dfs))
            df = df.reset_index(drop=True)
            df = df.drop_duplicates(keep="first")
            # HACK why are there NAs here?
            df = df[~df.isna()]

        if df.shape[0] != 0:
            def func(row):
                try:
                    return epoch_factory(self.files[row.exppath][f"epoch{int(row.number)}"])
                except Exception as e:
                    print(row.exppath)
                    raise e

            df["epoch"] = df.apply(lambda x:
                                   func(x),
                                   axis=1)
        else:
            raise Exception("No epochs returns")

        return df

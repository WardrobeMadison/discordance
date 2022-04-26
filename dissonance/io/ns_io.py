import pandas as pd
from pathlib import Path
from typing import Dict, List

import h5py


def read_unchecked_file(filepath:Path):
    """Read start dates to exclude. Header is startdate"""
    startdates = set()
    with open(filepath, "r") as fin:
        fin.readline()
        startdates.add(fin.readline().strip())

    return startdates

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

pctcntrst = pd.DataFrame(
    columns = "lightamplitude lightmean pctcontrast".split(),
    data = [
    [-0.001,0.005,-25],
    [-0.003,0.005,-50],
    [-0.005,0.005,-100],
    [0.001,0.005,25],
    [0.003,0.005,50],
    [0.005,0.005,100],
    [0.002,0.007,25],
    [0.004,0.007,50],
    [0.005,0.007,75],
    [0.007,0.007,100],
    [-0.002,0.007,-25],
    [-0.004,0.007,-50],
    [-0.005,0.007,-75],
    [-0.007,0.007,-100],
    [-0.002,0.006,-25],
    [-0.003,0.006,-50],
    [-0.006,0.006,-100],
    [0.002,0.006,25],
    [0.003,0.006,50],
    [0.006,0.006,100],
    [-0.006,0.006,-100],
    [0.002,0.005,50],
    [0.004,0.005,75],
    [-0.004,0.005,-75],
    [0.005,0.006,75],
    [-0.005,0.006,-75],
    [0.005,0,0],
    [0.006,0,0]])

# LED, AMP
rstarrmap = pd.DataFrame(
    columns = "led lightamplitude rstarr".split(),
    data = [
        ("Green LED", 0.007, 5),
        ("Green LED", 0.014, 10),
        ("Green LED", 0.0121, 10),
        ("Green LED", 0.006, 5),
        ("Green LED", 0.003, 0.025),
        ("Green LED", 0.006, 0.05),
        ("Green LED", 0.012, 0.1),
        ("Green LED", 0.024, 0.2),
        ("Green LED", 0.048, 0.4),
        ("Green LED", 0.096, 0.8),
        ("Green LED", 0.192, 1.6),
        ("Green LED", 0.384, 3.2),
        ("Green LED", 0.015, 0.1),
        ("Green LED", 0.03, 0.2),
        ("Green LED", 0.06, 0.4),
        ("Green LED", 0.12, 0.8),
        ("Green LED", 0.24, 1.6),
        ("Green LED", 0.48, 3.2),
        ("Green LED", 0.004, 0.025),
        ("Green LED", 0.008, 0.05),
        ("Green LED", 0.016, 0.1),
        ("Green LED", 0.032, 0.2),
        ("Green LED", 0.064, 0.4),
        ("Green LED", 0.128, 0.8),
        ("Green LED", 0.256, 1.6),
        ("Green LED", 0.512, 3.2),
        ("Green LED", 0.007, 0.05),
        ("Green LED", 0.014, 0.1),
        ("Green LED", 0.028, 0.2),
        ("Green LED", 0.056, 0.4),
        ("Green LED", 0.112, 0.8),
        ("Green LED", 0.224, 1.6),
        ("Green LED", 0.448, 3.2),
        ("Green LED", 0.896, 6.4),
        ("Green LED", 0.768, 6.4),
        ("Green LED", 0.0074, 0.05),
        ("Green LED", 0.0148, 0.1),
        ("Green LED", 0.006, 5),
        ("Green LED", 0.007, 5),
        ("Green LED", 0.012, 10),
        ("Green LED", 0.013, 10),
        ("Green LED", 0.014, 10),
        ("Green LED", 0.0121, 10),
        ("Green LED", 0.04, 3.25)])

def convert_to_rstarr(led, lightamplitude):
    if led == "Green LED":
        try:
            return rstarrmap.loc[
                (rstarrmap.led == led) 
                & (rstarrmap.lightamplitude == lightamplitude)].iloc[0,-1]
        except:
            print("MISSING", led, lightamplitude)
            return 0.0
    else:
        return 0.0
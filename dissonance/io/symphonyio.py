import datetime
import logging
import re
from pathlib import Path
from typing import Dict, Iterator

import h5py
import numpy as np
import pandas as pd
from dissonance.funks import detect_spikes

logger = logging.getLogger(__name__)

def get_rstarr_map():
    rstarrdf = pd.read_csv(
        Path(__file__).parent.parent.parent / "data/rstarrmap.txt", 
        delimiter="\t",
        parse_dates=["startdate", "enddate"],
        dtype=dict(
            protocolname=str,
            led=str,
            lightamplitude=float,
            lightamplitude_rstarr=float,
            lightmean=float,
            lightmean_rstarr=float))
    rstarrmap = dict()
    for _, row in rstarrdf.iterrows():
        rstarrmap[(row["protocolname"], row["led"], row["lightamplitude"], row["lightmean"])] = (
            row["lightamplitude_rstarr"], row["lightmean_rstarr"])
    return rstarrmap

RSTARRMAP = get_rstarr_map()
S1 = np.dtype("|S1")


def convert_if_bytes(attr):
    if isinstance(attr, np.bytes_):
        return attr.decode()
    else:
        return attr


class GroupBase:

    re_name = ""

    def __init__(self, parent: h5py.Group):
        self.parent = parent
        for name in self.parent:
            if self.re_name.match(name):
                self._name = name

        self.group: h5py.Group = parent[name]

    @property
    def name(self) -> str:
        return self._name


class Experiment(GroupBase):

    re_name = re.compile(r"experiment-.*")

    def __init__(self, parent: h5py.Group):
        super().__init__(parent)

    def name(self):
        return self._name

    @property
    def children(self):
        for name in self.group["epochGroups"]:
            yield Cell(self.group[f"epochGroups/{name}"])


class Cell:

    RE_DATE = re.compile(r"^.*(\d{4}-?\d{2}-?\d{2})(\w\d?).*$")

    def __init__(self, group: h5py.Group):
        self.group = group
        self.h5name = group.name
        self.name = "epochGroup"

    def __str__(self):
        return str(self.group)

    @property
    def cellname(self):
        val = convert_if_bytes(self.group["source"].attrs["label"])
        if isinstance(val, str):
            return val
        else:
            return "MissingCellName"

    @property
    def celltype(self):
        val = convert_if_bytes(self.group["source/properties"].attrs["type"])
        if isinstance(val, str):
            return val
        else:
            return "MissingCellType"

    @property
    def cellkey(self):
        filepath = Path(self.group.file.filename)

        name = filepath.stem
        matches = self.RE_DATE.match(name)
        prefix = matches[1].replace("-", "") + matches[2]

        return f"{prefix}_{self.cellname}"

    @property
    def children(self):
        for name in self.group["epochBlocks"]:
            yield Protocol(self.group[f"epochBlocks/{name}"])


# TODO turn into abstract factor distinguished by protocol.
#   Set a property that has all params needed to write out here. Not in the read method below.
class Protocol:

    re_name = re.compile(r".*edu\.wisc\.sinhalab\.protocols\.([\w\d ]+)-.*$")

    def __init__(self, group: h5py.Group):
        self.group = group
        self.h5name = group.name
        self.name = self.re_name.match(group.name)[1]

    def __str__(self):
        return f"EpochBlock({self.name})"

    def __iter__(self):
        for key, val in self.group["protocolParameters"].attrs.items():
            yield key, convert_if_bytes(val)

    def __getitem__(self, value):
        val = self.group["protocolParameters"].attrs[value]
        return convert_if_bytes(val)

    def get(self, value, default=None):
        val = self.group["protocolParameters"].attrs.get(value, default)
        return convert_if_bytes(val)

    @property
    def children(self):
        for name in self.group["epochs"]:
            yield Epoch(self.group[f"epochs/{name}"])


class Epoch:

    re_responses = re.compile(r"^([\w\d ]+)-.*$")

    def __init__(self, group: h5py.Group):
        self.group = group
        self.h5name = group.name
        self.name = "epoch"

        self._backgrounds = dict()
        for name in self.group["backgrounds"]:
            background = Background(self.group[f"backgrounds/{name}"])
            self._backgrounds[background.name] = background

    def __str__(self):
        return f"Epoch({self.startdate})"

    @property
    def tracetype(self):
        val = self._backgrounds["Amp1"]["value"]
        if float(val) == 0.0:
            return "spiketrace"
        else:
            return "wholetrace"

    @property
    def holdingpotential(self):
        val = self._backgrounds["Amp1"]["value"]
        if self.tracetype == "spiketrace":
            return "nan"
        elif val < 0:
            return "excitation"
        else:
            return "inhibitiion"

    @property
    def backgrounds(self):
        return self._backgrounds

    @property
    def responses(self):
        for name in self.group["responses"]:
            yield Response(self.group[f"responses/{name}"])

    @property
    def startdate(self):
        dotNetTime = self.group.attrs['startTimeDotNetDateTimeOffsetTicks']
        return datetime.datetime(1, 1, 1) + datetime.timedelta(microseconds=int(dotNetTime // 10))

    @property
    def enddate(self):
        dotNetTime = self.group.attrs['endTimeDotNetDateTimeOffsetTicks']
        return datetime.datetime(1, 1, 1) + datetime.timedelta(microseconds=int(dotNetTime // 10))

    @property
    def stimuli(self):
        for name in self.group["stimuli"]:
            yield Stimulus(self.group[f"stimuli/{name}"])

    @property
    def ndf(self):
        return self.group["protocolParameters"].attrs.get("ndf", "None")

class Background:

    re_name = re.compile(r"^([\w\d ]+)-.*$")

    def __init__(self, group: h5py.Group):
        self.group = group
        self.h5name = group.name
        self.name = self.re_name.match(
            group.name.split("/")[-1])[1]

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

    def __getitem__(self, value):
        return convert_if_bytes(self.group.attrs[value])

    def __iter__(self) -> Iterator[Dict[str, object]]:
        for key, value in self.group.attrs.items():
            return key, convert_if_bytes(value)


class Response:

    re_name = re.compile(r"^([\w\d ]+)-.*$")

    def __init__(self, group: h5py.Group):
        self.group = group
        self.h5name = group.name
        self.name = self.re_name.match(
            group.name.split("/")[-1])[1]

        self._parameters: Dict = {
            "samplerate": self.group.attrs["sampleRate"],
            "samplerateunits": self.group.attrs["sampleRateUnits"]
        }

    def __str__(self):
        return f"Response({self.name})"

    def __repr__(self):
        return f"Response({self.name})"

    @property
    def data(self):
        vals = np.array(self.group["data"][:], dtype=[
                        ('v', '<f8'), ('units', '<U16')])
        return vals['v']

    @property
    def parameters(self) -> Dict:
        return self._parameters

    def __getitem__(self, value):
        return self._parameters[value]

    def __iter__(self) -> Iterator[Dict[str, object]]:
        for key, value in self._parameters:
            yield key, convert_if_bytes(value)

    def get(self, value, default):
        return self._parameters.get(value, default)


class Stimulus:

    re_name = re.compile(r"^([a-zA-Z0-9_ ]*)-.*$")

    def __init__(self, group: h5py.Group):
        self.group = group
        self.h5name = group.name
        self.name = self.re_name.match(
            self.group.name.split("/")[-1])[1]

        self._parameters = self.group["parameters"].attrs

    @property
    def parameters(self):
        return self._parameters

    def __getitem__(self, value):
        return self._parameters[value]

    def __iter__(self) -> Iterator[Dict[str, object]]:
        for key, val in self.group["parameters"].attrs.items():
            yield key, convert_if_bytes(val)


class SymphonyReader:

    def __init__(self, path):
        self.finpath = path
        self.fin = h5py.File(path)
        self.exp = Experiment(self.fin)
        self.fout = None

    def reader(self):
        ii = 0
        for cell in self.exp.children:
            for protocol in cell.children:
                for epoch in protocol.children:
                    yield cell, protocol, epoch

    def to_h5(self, outputpath: Path):
        try:
            self.fout = h5py.File(outputpath, mode="w")
            expgrp = self.fout.create_group("experiment")
            for ii, (cell, protocol, epoch) in enumerate(self.reader()):

                epochgrp = expgrp.create_group(f"epoch{ii}")

                # ADD EPOCH ATTRIBUTES
                self._update_attrs(protocol, cell, epoch, epochgrp)

                # ADD RESPONSE DATA - CACHE SPIKES
                self._update_response(epoch, epochgrp)

                # ADD GROUP FOR EACH STIMULUS
                self._update_stimuli(epoch, epochgrp)

        except Exception as e:
            if self.fout is not None:
                self.fout.close()
            raise e
        finally:
            self.fout.close()

    def update_metadata(self, outputpath, attrs=False, responses=False, stimuli=False):
        try:
            self.fout = h5py.File(outputpath, mode="r+")
            expgrp = self.fout["experiment"]
            for ii, (cell, protocol, epoch) in enumerate(self.reader()):

                epochgrp = expgrp[f"epoch{ii}"]

                # ADD EPOCH ATTRIBUTES
                if attrs:
                    self._update_attrs(protocol, cell, epoch, epochgrp)

                # ADD RESPONSE DATA - CACHE SPIKES
                if responses:
                    self._update_response(epoch, epochgrp)

                # ADD GROUP FOR EACH STIMULUS
                if stimuli:
                    self._update_stimuli(epoch, epochgrp)

        except Exception as e:
            if self.fout is not None:
                self.fout.close()
            raise e

        self.fout.close()

    def update_rstarr(self, outputpath):
        try:
            self.fout = h5py.File(outputpath, mode="r+")
            expgrp = self.fout["experiment"]
            for ii, (cell, protocol, epoch) in enumerate(self.reader()):

                epochgrp = expgrp[f"epoch{ii}"]
                try:
                    del epochgrp.attrs["lightamplitude"]
                except KeyError:
                    ...
                try:
                    del epochgrp.attrs["lightmean"]
                except KeyError:
                    ...
                try:
                    del epochgrp.attrs["lightamplitudeSU"]
                except KeyError:
                    ...
                try:
                    del epochgrp.attrs["lightmeanSU"]
                except KeyError:
                    ...

                self._rstarr_conversion(protocol, epoch, epochgrp)

        except Exception as e:
            if self.fout is not None:
                self.fout.close()
            raise e

        self.fout.close()

    def _update_stimuli(self, epoch: h5py.Group, epochgrp: h5py.Group):
        for stimuli in epoch.stimuli:
            stimds = epochgrp.create_group(stimuli.name)
            for key, val in stimuli:
                stimds.attrs[key.lower()] = val

    def _update_response(self, epoch: h5py.Group, epochgrp: h5py.Group):
        for response in epoch.responses:
            values = response.data
            ds = epochgrp.create_dataset(
                name=response.name, data=values, dtype=float)

            # for key, val in response:
            #    ds.attrs[key] = val

            ds.attrs["path"] = response.h5name

            if epoch.tracetype == "spiketrace":
                spikes, violationidx = detect_spikes(values)

                spds = epochgrp.create_dataset(
                    name="Spikes",
                    data=spikes,
                    dtype=float)

                spds.attrs["violation_idx"] = (
                    violationidx.astype(float))

    def _update_attrs(self, protocol: h5py.Group, cell: h5py.Group, epoch: h5py.Group, epochgrp: h5py.Group):
        # ADD EPOCH ATTRIBUTES
        epochgrp.attrs["path"] = epoch.h5name
        epochgrp.attrs["cellname"] = cell.cellkey
        epochgrp.attrs["celltype"] = cell.celltype
        epochgrp.attrs["genotype"] = "PleaseAddGenotype"
        epochgrp.attrs["tracetype"] = epoch.tracetype
        epochgrp.attrs["protocolname"] = protocol.name
        epochgrp.attrs["startdate"] = str(epoch.startdate)
        epochgrp.attrs["enddate"] = str(epoch.enddate)
        epochgrp.attrs["interpulseinterval"] = protocol["interpulseInterval"]
        epochgrp.attrs["led"] = protocol["led"]

        self._rstarr_conversion(protocol, epoch, epochgrp)

        epochgrp.attrs["numberofaverages"] = protocol.get(
            "numberOfAverages", 0.0)
        epochgrp.attrs["pretime"] = protocol.get("preTime", 0.0)
        epochgrp.attrs["backgroundval"] = epoch.backgrounds["Amp1"]["value"]
        epochgrp.attrs["stimtime"] = protocol.get("stimTime", 0.0)
        epochgrp.attrs["samplerate"] = protocol.get("sampleRate", 0.0)
        epochgrp.attrs["tailtime"] = protocol.get("tailTime", 0.0)
        epochgrp.attrs["ndf"] = epoch.ndf
        epochgrp.attrs["holdingpotential"] = epoch.holdingpotential

    def _rstarr_conversion(self, protocol, epoch, epochgrp):
        # SOMTIMES LIGHT AMPLITUDE IS CALLED SOMETHING ELSE
        lightamp = protocol.get("lightAmplitude", None)
        if lightamp is None:
            lightamp = protocol.get("firstLightAmplitude", None)
        if lightamp is None:
            lightamp = 0.0
            logging.info(f"{str(epoch.startdate)}: no lightamplitude.")

        lightmean = protocol.get("lightMean", None)
        if lightmean is None:
            lightmean = 0.0
            logging.info(f"{str(epoch.startdate)}: no lightmean.")

        epochgrp.attrs["lightamplitudeSU"] = lightamp
        epochgrp.attrs["lightmeanSU"] = lightmean

        try:
            epochgrp.attrs["lightamplitude"], epochgrp.attrs["lightmean"] = (
                RSTARRMAP[
                    (protocol.name, protocol["led"], lightamp, lightmean)])
        except KeyError:
            logging.warning(
                f"RStarrConversionError: {','.join(map(str, (protocol.name, protocol['led'],lightamp, lightmean)))}")
            epochgrp.attrs["lightamplitude"], epochgrp.attrs["lightmean"] = -10000, -10000

    def to_db(self):
        ...

"""
From HDF to other formats for simpler data analysis
Datable structure: index := Index, ExperimentName, CellName, ProtocolName, SplitVariable, ResponseVariable
Index, ExperimentName, CellName, ProtocolName, SplitVariable, ResponseVariable, Time, ResponseValue
MetaData structure:
Index, ExperimentName, Device, Gain, Etc...
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
import datetime
import json
import re
from os import path
from pathlib import Path
from typing import Dict, Iterator

import h5py
import numpy as np

from ..funks import detect_spikes
from .symphonytrace import SymphonyEpoch

RE_PID = re.compile(r"^edu.wisc.sinhalab.protocols.(\w+):protocolID$")
RE_PP = re.compile(
    r"^edu.wisc.sinhalab.protocols.(\w+):protocolParameters:(\w+)")

# experiment
# epochgroups
# epochgroup
# epochblock
# protocols
# epochs
# backgrounds
# responses
# stimuli

class GroupBase:

    re_name = ""
    def __init__(self, parent: h5py.Group):
        self.parent = parent
        for name in self.parent:
            if self.re_name.match(name):
                self._name  = name

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
            yield EpochGroup(self.group[f"epochGroups/{name}"])

class EpochGroup:

    def __init__(self, group: h5py.Group):
        self.group = group
        self.h5name = group.name
        self.name = "epochGroup"

    @property
    def children(self):
        for name in self.group["epochBlocks"]:
            yield EpochBlock(self.group[f"epochBlocks/{name}"])


class EpochBlock:
    re_name = re.compile(r"edu\.wisc\.sinhalab\.protocols\.(.*)-.*$")

    def __init__(self, group: h5py.Group):
        self.group = group
        self.h5name = group.name
        self.name = self.re_name.match(group.name)[1]

    @property
    def children(self):
        for name in self.group["epochs"]:
            yield Epoch(self.group[f"epochs/{name}"])

    @property
    def protocolparameters(self):
        ...

class Epoch:

    def __init__(self, group: h5py.Group):
        self.group = group
        self.h5name = group.name
        self.name = "epoch"

    @property
    def children(self):
        for name in self.group["epochs"]:
            yield Epoch(self.group[f"epochs/{name}"])

    @property
    def protocolparameters(self):
        ...

@dataclass
class Backgrounds:
    ...

@dataclass
class EpochProtocolParameters:
    ...

@dataclass
class Response:
    ...


class SymphonyReader:
    """
    Convert "raw" h5 files from Symphony for data to be used by dissonance.
    """
    time_map = {
        'startTimeDotNetDateTimeOffsetTicks': 'startDate',
        'endTimeDotNetDateTimeOffsetTicks': 'endDate',
        'creationTimeDotNetDateTimeOffsetTicks': 'creationDate',
    }

    meta_excludes = (
        'startTimeDotNetDateTimeOffsetOffsetHours',
        'uuid',
        'creationTimeDotNetDateTimeOffsetOffsetHours',
        'endTimeDotNetDateTimeOffsetOffsetHours'
    )

    def __init__(self, symphonyfilepath):
        self.symphonyfilepath = symphonyfilepath

    def _to_datetime(self, dotNetTime):
        if isinstance(dotNetTime, str):
            dotNetTime = int(dotNetTime)
        return datetime.datetime(1, 1, 1) + datetime.timedelta(microseconds=int(dotNetTime // 10))

    def _read_file(self, filename):
        try:
            f = h5py.File(filename, "r")
        except FileNotFoundError:
            raise Exception(f"File {filename} not found. Redirect.")
        except Exception as e:
            raise e
        else:
            return f

    def _cells(self):
        exp_name = [x for x in list(self.fin) if "experiment" in x][0]
        path_epochgroups = path.join(exp_name, 'epochGroups')

        for cell in self.fin[path_epochgroups]:  # cellName
            path_cell = path.join(path_epochgroups, cell)
            yield self.fin[path_cell]

    def _protocols(self, cell):
        for protocol in cell['epochBlocks']:
            path_protocol = path.join('epochBlocks', protocol)
            yield cell[path_protocol]

    def _epochs(self, protocol):
        for epoch in protocol['epochs']:
            path_epoch = path.join('epochs', epoch)
            yield protocol[path_epoch]

    def _reader(self) -> Iterator[SymphonyEpoch]:
        for cell in self._cells():

            # PARSE CELL INFORMATION
            meta_cell = self._get_all_metadata(cell)
            cellname = meta_cell.get("epochGroup:source:label")
            celltype = meta_cell.get('epochGroup:source:properties:type')

            if not isinstance(celltype, str):
                print(f"Couldn't find celltype for {self.fin, cellname}.")
                celltype = None

            for p, protocol in enumerate(self._protocols(cell)):
                print(protocol)
                meta_protocol = self._get_all_metadata(protocol)
                protocoldict = dict()

                # HACK CONVERT PROTOCOL PARAMETERS. Do this in meta_protocol on first pass
                for key, val in meta_protocol.items():
                    if RE_PID.match(key) is not None:
                        protocoldict["protocolname"] = RE_PID.match(key)[1]
                    elif RE_PP.match(key) is not None:
                        protocoldict[RE_PP.match(key)[2].lower()] = val

                # TRAVERSE EPOCHS
                for i, epoch in enumerate(self._epochs(protocol)):
                    # grab responses (sub folders with recursion)
                    # grab stimulus
                    # grab backgrounds
                    meta_epoch = self._get_all_metadata(epoch)
                    response_dict = self._get_responses(epoch['responses'])

                    # HACK CAN'T GET LIGHT AMPLITUDE PARSING WORKING
                    lightamp = protocoldict.get("lightamplitude")
                    if lightamp is None:
                        lightamp = meta_epoch.get(
                            "protocolParameters:lightAmplitude")

                    yield SymphonyEpoch(
                        path=epoch.name,
                        cellname=cellname,
                        celltype=celltype,
                        tracetype="spiketrace" if meta_epoch["backgrounds:Amp1:value"] == 0.0 else "wholetrace",
                        protocolname=protocoldict["protocolname"],
                        startdate=str(meta_epoch["startDate"]),
                        enddate=str(meta_epoch["endDate"]),
                        interpulseinterval=protocoldict["interpulseinterval"],
                        led=protocoldict["led"],
                        lightamplitude=lightamp,
                        lightmean=protocoldict.get("lightmean", 0.0),
                        numberofaverages=protocoldict.get("numberofaverages", 0.0),
                        pretime=protocoldict.get("pretime", 0.0),
                        stimtime=protocoldict.get("stimtime", 0.0),
                        samplerate=protocoldict.get("samplerate", 0.0),
                        tailtime=protocoldict.get("tailtime", 0.0),
                        responses=response_dict
                    )

                #print(f"{cellname}, Protocol {p}: {i} epochs.")

    def _get_responses(self, responses) -> Dict:
        response_dict = {}
        for response in responses:
            grp = responses[response]

            name = self._group_name(grp)
            metadata = self._get_all_metadata(grp)

            response_dict[name] = {
                'path': grp.name,
                'attrs': metadata
            }
        return response_dict

    def _get_group_metadata(self, group, metadata, level):
        for key, val in group.attrs.items():
            if key in self.meta_excludes:
                continue
            elif key in self.time_map.keys():
                new_key = self.time_map[key]
                if level == '':
                    metadata[f"{new_key}"] = self._to_datetime(val)
                else:
                    metadata[f"{level}:{new_key}"] = self._to_datetime(val)
            elif level:
                if type(val) is np.bytes_:
                    metadata[f"{level}:{key}"] = val.decode()
                else:
                    metadata[f"{level}:{key}"] = val
            else:
                metadata[f"{new_key}"] = val
        return metadata

    def _convert_vals(self, val):
        try:
            return val.decode()
        except (UnicodeDecodeError, AttributeError):
            return val

    def _get_all_metadata(self, group, metadata=None, level=None):

        if level:
            tlevel = self._group_name(group)
            if tlevel != level:
                level = ":".join([level, self._group_name(group)])
            if level[0] == ":":
                level = level[1:]

        else:
            level = self._group_name(group)
            level = '' if level == 'epoch' else level
            try:
                if level[0] == ":":
                    level = level[1:]
            except IndexError:
                pass

        metadata = metadata if metadata else dict()
        metadata = self._get_group_metadata(group, metadata, level)
        for name in group:
            subgroup = group[name]
            if self._is_group(subgroup):
                metadata = self._get_all_metadata(subgroup, metadata, level)
        return metadata

    def _group_name(self, group):
        name = group.name.split("/")[-1].split("-")[0]
        if 'edu.washington.riekelab.protocols' in name:
            name = name.split('.')[-1]
        return name

    def _is_group(self, group):
        name = self._group_name(group)
        is_link = name in ('epoch', 'experiment', 'epochBlocks',
                           'epochBlock', 'epochGroup', 'epochGroups', 'parent', 'sources')
        is_group = isinstance(group, h5py._hl.group.Group)

        return bool(bool(is_group) & ~bool(is_link))

    def to_h5(self, outputpath: Path):
        try:
            self.fin = h5py.File(self.symphonyfilepath, "r")
            fout = h5py.File(str(outputpath), "w")
            params = [
                "path",
                "cellname",
                "startdate",
                "celltype",
                "tracetype",
                "protocolname",
                "enddate",
                "interpulseinterval",
                "led",
                "lightamplitude",
                "lightmean",
                "numberofaverages",
                "pretime",
                "stimtime",
                "samplerate",
                "tailtime"]

            expgrp = fout.create_group("experiment")
            for ii, symepoch in enumerate(self._reader()):

                # CREATE NEW GROUP
                epochgrp = expgrp.create_group(f"epoch{ii}")

                # ADD PARAMS FROM SYMPHONY TRACE
                # TODO JUST CONVERT DATACLASS TO DICT
                for param in params:
                    try:
                        epochgrp.attrs[param] = getattr(symepoch, param)
                    except TypeError:
                        epochgrp.attrs[param] = str(getattr(symepoch, param))

                # WRITE OUT RESPONSES
                for responsename, val in symepoch.responses.items():
                    # CREATE DATASET FOR A RESPONSE
                    data = np.array(self.fin[val["path"]]['data'])
                    values = np.fromiter([x[0] for x in data], dtype=float)

                    ds = epochgrp.create_dataset(
                        name=responsename, data=values, dtype=float)
                    ds.attrs["path"] = val["path"]

                    # CREATE SPIKE DATASET FOR A RESPONSE
                    if symepoch.tracetype == "spiketrace":
                        epochgrp.attrs["tracetype"] = "spiketrace"
                        spikeinfo = detect_spikes(values)
                        ds.attrs["sp"] = spikeinfo.sp.astype(float)
                        ds.attrs["spike_amps"] = spikeinfo.spike_amps.astype(
                            float)
                        ds.attrs["max_noise_peak_time"] = spikeinfo.max_noise_peak_time.astype(
                            float)
                        ds.attrs["min_spike_peak_idx"] = spikeinfo.min_spike_peak_idx.astype(
                            float)
                        ds.attrs["violation_idx"] = spikeinfo.violation_idx.astype(
                            float)

        except Exception as e:
            raise e

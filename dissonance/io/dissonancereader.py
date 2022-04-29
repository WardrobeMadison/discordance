import multiprocessing
from pathlib import Path
from typing import List
import multiprocessing as mp
from pathos.multiprocessing import ProcessingPool
import re

import h5py

from dissonance.epochtypes.baseepoch import DissonanceParams

from .. import epochtypes as et


RE_DATE = re.compile(r"^.*(\d{4}-\d{2}-\d{2})(\w\d?).*$")


class DissonanceReader:

    def __init__(self, filepaths: List[Path]):
        self.experimentpaths = filepaths

    def h5_to_epochs(self, filepath, **kwargs):
        try:
            matches = RE_DATE.match(str(filepath))
            prefix = matches[1].replace("-", "") + matches[2]

            h5file = h5py.File(str(filepath), "a")
            traces = []
            experiment = h5file["experiment"]
            for ii, epochname in enumerate(experiment):
                epoch = experiment[epochname]

                condition = all([epoch.attrs[key] == val for key,val in kwargs.items()])
                if condition:
                    number=f"{ii+1:04d}"

                    # GET PARAMETERS
                    #params = et.DissonanceParams()
                    #disargs = {
                    #    key: val
                    #    for key, val in epoch.attrs.items()
                    #    if key in DissonanceParams.__annotations__.keys()}
                    params = et.DissonanceParams(**epoch.attrs)

                    # SEPARATE TRACES
                    resp = epoch["Amp1"]
                    if params.tracetype == "spiketrace":
                        spikes = et.EpochSpikeInfo(
                            resp.attrs["sp"],
                            resp.attrs["spike_amps"],
                            resp.attrs["min_spike_peak_idx"],
                            resp.attrs["max_noise_peak_time"],
                            resp.attrs["violation_idx"]
                        )

                        trace = et.SpikeEpoch(
                            epoch.name,
                            params,
                            spikes,
                            resp,
                            number=number)
                    else:
                        trace = et.WholeEpoch(
                            epoch.name,
                            params,
                            resp,
                            number=number)

                    traces.append(trace)
            print(f"{len(traces)} traces")
            return traces
        except Exception as e:
            print(filepath)
            print(e)
            return []

    @staticmethod
    def init_mp(l):
        global lock
        lock = l

    def to_epochs(self, **kwargs) -> List:
        traces = []
        #l = multiprocessing.Lock()
        #with mp.Pool(processes=nprocesses, initializer=self.init_mp, initargs=(1,)) as p:
        #    for exptraces in p.imap(self.h5_to_epochs, self.experimentpaths):
        #        traces.extend(exptraces)
        for ii, filepath in enumerate(self.experimentpaths):
            print(f"Loading {ii+1} / {len(self.experimentpaths)}: {filepath}")
            traces.extend(self.h5_to_epochs(filepath, **kwargs))
        return traces

from pathlib import Path
from typing import List
#from multiprocessing import Pool
import dill
from pathos.multiprocessing import ProcessingPool
import re

import h5py

from .. import epochtypes as et


RE_DATE = re.compile(r"^.*(\d{4}-\d{2}-\d{2})(\w\d?).*$")


class DissonanceReader:

    def __init__(self, filepaths: List[Path]):
        self.experimentpaths = filepaths

    def h5_to_epochs(self, filepath):
        try:
            matches = RE_DATE.match(str(filepath))
            prefix = matches[1].replace("-", "") + matches[2]

            h5file = h5py.File(str(filepath), "a")
            traces = []
            experiment = h5file["experiment"]
            for ii, epochname in enumerate(experiment):
                number=f"{prefix}_{ii+1:04d}"
                epoch = experiment[epochname]
                params = et.DissonanceParams()

                # GET PARAMETERS
                for key, val in epoch.attrs.items():
                    setattr(params, key.lower(), val)

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
            return traces
        except Exception as e:
            print(filepath)
            print(e)
            return []

    def to_epochs(self, nprocesses=4) -> List:
        traces = []
        #with ProcessingPool(processes=nprocesses) as p:
            #for exptraces in p.imap(self.h5_to_epochs, self.experimentpaths):
                #traces.extend(exptraces)
        for filepath in self.experimentpaths:
            traces.extend(self.h5_to_epochs(filepath))
        return traces

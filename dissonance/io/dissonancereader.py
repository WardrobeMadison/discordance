from pathlib import Path
from typing import List

import h5py

from .. import epochtypes as et


class DissonanceReader:

    def __init__(self, filepaths: List[Path]):
        self.experimentpaths = filepaths

    def to_epochs(self) -> List:
        traces = []
        for filepath in self.experimentpaths:
            h5file = h5py.File(filepath, "r")

            experiment = h5file["experiment"]
            for epochname in experiment:
                epoch = experiment[epochname]
                params = et.DissonanceParams()

                # GET PARAMETERS
                for key, val in epoch.attrs.items():
                    setattr(params, key.lower(), val)

                # SEPARATE TRACES
                if params.tracetype == "spiketrace":
                    resp = epoch["Amp1"]
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
                        resp)
                else:
                    trace = et.WholeEpoch(
                        epoch.name,
                        params,
                        resp)
                traces.append(trace)
        return traces

import h5py
from typing import Dict 
import numpy as np

from .basetrace import BaseTrace
from ..funks.spike_detection import TraceSpikeResult

class SpikeTrace(BaseTrace):

	type = "SpikeTrace"

	def __init__(self, h5file: h5py.File, epochpath: str,
			parameters:Dict[str, object]=None, responses: Dict=None):

		super().__init__(h5file, epochpath, parameters, responses)
		self.epochresponsepath = responses["Amp1"]["path"]
		self._spikes = None

	@property
	def spikes(self) -> TraceSpikeResult:
		...
		if self._spikes is None: 
			spikedict = self.responses["Amp1"]["spikes"]
			self._spikes = TraceSpikeResult(
				spikedict["sp"],
				spikedict["spike_amps"],
				spikedict["min_spike_peak_idx"],
				spikedict["max_noise_peak_time"],
				spikedict["violation_idx"]
			)
		return self._spikes



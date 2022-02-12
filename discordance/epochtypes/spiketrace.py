from __future__ import annotations

from dataclasses import dataclass
from typing import List

import numpy as np
from discordance.funks.psth import calculate_psth
from h5py._hl.dataset import Dataset

from .ns_epochtypes import DiscordanceParams, TraceSpikeResult
from .basetrace import ITrace, Traces

class SpikeTrace(ITrace):

	def __init__(self, epochpath: str,
			parameters:DiscordanceParams=None, 
			spikes:TraceSpikeResult=None,
			response: Dataset=None):

		super().__init__(epochpath, parameters, response)
		self._spikes = spikes
		self._psth = None

	@property
	def spikes(self) -> TraceSpikeResult:
		return self._spikes

	@property
	def psth(self) -> np.array:
		if self._psth is None:
			self._psth = calculate_psth(self)
		return self._psth

	@property
	def type(self) -> str:
		return "spiketrace"

class SpikeTraces(Traces):

	type = "spiketrace"

	def __init__(self, key, traces: List[SpikeTrace]):
		super().__init__(traces)

		self.key = key
		self._psth:np.array = None

	@property
	def psth(self):
		inc = 100
		if self._psth is None:
			# FILL TAIL OF PSTH'S WITH 0'S SO ALL OF SAME SIZE

			cnt = 0
			for trace in self._traces:
				if len(trace.psth) > 0 and trace.psth is not None:
					cpsth = np.pad(trace.psth, (0, int(self.trace_len // inc - len(trace.psth))))
					if cnt == 0: psths = cpsth
					else: psths += cpsth
					cnt += 1

			if cnt != 0: self._psth = psths / cnt

		return self._psth


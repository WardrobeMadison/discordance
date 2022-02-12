from __future__ import annotations

from abc import ABC, abstractproperty
from typing import Dict, List

import numpy as np
from h5py._hl.dataset import Dataset

from . import ns_epochtypes as ns

class ITrace(ABC):

	def __init__(self, epochpath: str, params: ns.DiscordanceParams, response: Dataset):

		self._epochpath:str = epochpath
		self._response_ds = response

		self.protocolname = params.protocolname
		self.cellname = params.cellname
		self.celltype = params.celltype
		self.path = params.path
		self.amp = params.amp
		self.interpulseinterval = params.interpulseinterval
		self.led = params.led
		self.lightamplitude = params.lightamplitude
		self.lightmean = params.lightmean
		self.numberofaverages = params.numberofaverages
		self.samplerate = params.samplerate
		self.pretime = params.pretime * 10
		self.stimtime = params.stimtime * 10
		self.tailtime = params.tailtime * 10
		self.startdate = params.startdate 
		self.enddate = params.enddate

	def __eq__(self, other) -> bool:
		return  self.enddate == other.enddate

	def __ne__(self, other) -> bool:
		return self.enddate != other.enddate

	def __str__(self):
		return f"Epoch(cell_name={self.cellname}, start_date={self.startdate})"

	def __len__(self):
		try:
			return int(self.pretime + self.stimtime + self.tailtime)
		except TypeError as e:
			print(e)
			return 0.0

	@property
	def values(self):
		return self._response_ds[:]
	
	@property
	@abstractproperty
	def type(self):
		...

class Traces(ABC):

	def __init__(self, traces = List[ITrace]):
		# HACK key should be daterange, convert dates from string to datetimes
		if len(traces) > 0:
			self.key = traces[0].startdate 
		else: 
			self.key = None
		self._traces:List[ITrace]= traces
		self._trace_len:int=None
		self._celltypes:List[str] = None
		self._interpulseintervals = None
		self._leds = None
		self._cellnames:List[str] = None
		self._protocolnames:List[str] = None
		self._lightamplitudes:List[float] = None
		self._lightmeans:List[float] = None
		self._pretimes:List[float] = None
		self._samplerates:List[float] = None
		self._stimtimes:List[float] = None
		self._pretimes:List[float] = None
		self._tailtimes:List[float] = None
		self._startdates:List[str] = None
		self._enddates:List[str] = None
		self._values:np.array = None

	def __str__(self):
		return str(self.key)

	def __getitem__(self, val) -> ITrace:
		return self._traces[val]

	def __len__(self):
		return len(self._traces)

	@property
	def trace_len(self):
		if self._trace_len is None:
			#self._trace_len = max([len(e) for e in self._traces])
			# TODO HACK debug the above
			self._trace_len = int(max([len(e) for e in self._traces]))
		return self._trace_len

	@property
	def traces(self)-> List[ITrace]: return self._traces

	@property
	def values(self) -> np.array:
		# PAD ALL VALUES TO STRETCH INTO FULL ARRAY
		if self._values is None:
			self._values = np.vstack(
				[
					np.pad(trace.values, (0, self._trace_len - len(trace)))
					for trace in self._traces
				])
		return self._values

	@property
	def celltypes(self) -> List[str]:
		if self._celltypes is None:
			self._celltypes = list(
				map(
					lambda e: e.celltype,
					self._traces))
		return self._celltypes

	@property
	def protocolnames(self) -> List[str]:
		if self._protocolnames is None:
			self._protocolnames = list(
				map(
					lambda e: e.protocolname,
					self._traces))
		return self._protocolnames

	@property
	def cellnames(self) -> List[str]:
		if self._cellnames is None:
			self._cellnames = list(
				map(
					lambda e: 
					e.cellname,
					self._traces))
		return self._cellnames

	@property
	def lightamplitudes(self) -> List[float]:
		if self._lightamplitudes is None:
			self._lightamplitudes = list(
				map(
					lambda e: 
					e.lightamplitude,
					self._traces))
		return self._lightamplitudes

	@property
	def lightmeans(self) -> List[float]:
		if self._lightmeans is None:
			self._lightmeans = list(
				map(
					lambda e: 
					e.lightmean,
					self._traces))
		return self._lightmeans

	@property
	def pretimes(self) -> List[float]:
		if self._pretimes is None:
			self._pretimes = list(
				map(
					lambda e: 
					e.pretime,
					self._traces))
		return self._pretimes

	@property
	def samplerates(self) -> List[float]:
		if self._samplerates is None:
			self._samplerates = list(
				map(
					lambda e: 
					e.samplerate,
					self._traces))
		return self._samplerates

	@property
	def stimtimes(self) -> List[float]:
		if self._stimtimes is None:
			self._stimtimes = list(
				map(
					lambda e: 
					e.stimtime,
					self._traces))
		return self._stimtimes

	@property
	def pretimes(self) -> List[float]:
		if self._pretimes is None:
			self._pretimes = list(
				map(
					lambda e: 
					e.pretime,
					self._traces))
		return self._pretimes

	@property
	def tailtimes(self) -> List[float]:
		if self._tailtimes is None:
			self._tailtimes = list(
				map(
					lambda e: 
					e.tailtime,
					self._traces))
		return self._tailtimes

	@property
	def startdates(self) -> List[str]:
		if self._startdates is None:
			self._startdates = list(
				map(
					lambda e: 
					e.startdate,
					self._traces))
		return self._startdates

	@property
	def enddates(self) -> List[str]:
		if self._enddates is None:
			self._enddates = list(
				map(
					lambda e: 
					e.enddate,
					self._traces))
		return self._enddates

	@property
	def interpulseintervals(self) -> List[str]:
		if self._interpulseintervals is None:
			self._interpulseintervals = list(
				map(
					lambda e: 
					e.interpulseinterval,
					self._traces))
		return self._interpulseintervals

	@property
	def leds(self) -> List[str]:
		if self._leds is None:
			self._leds = list(
				map(
					lambda e: 
					e.led,
					self._traces))
		return self._leds


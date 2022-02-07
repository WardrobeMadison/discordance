from abc import ABC, abstractproperty, abstractmethod
from typing import Dict, Union
from datetime import datetime

from h5py._hl.files import File
import numpy as np

class BaseTrace:

	def __init__(self, h5file: File, epochpath: str,
			parameters:Dict[str, object]=None, responses: Dict=None):

		self.h5file = h5file
		self.epochpath = epochpath
		self.parameters = parameters
		self.responses = responses

		# TODO change protocol path parsed to just protocl parameters. Portcol itself will change
		self.cellname = self.parameters.get("CellName")
		self.lightamplitude = self.parameters.get("edu.wisc.sinhalab.protocols.LedPulse:protocolParameters:lightAmplitude")
		self.lightmean = self.parameters.get("edu.wisc.sinhalab.protocols.LedPulse:protocolParameters:lightMean")
		self.pretime = self.parameters.get("edu.wisc.sinhalab.protocols.LedPulse:protocolParameters:preTime")
		self.samplerate = self.parameters.get("edu.wisc.sinhalab.protocols.LedPulse:protocolParameters:sampleRate")
		self.stimtime = self.parameters.get("edu.wisc.sinhalab.protocols.LedPulse:protocolParameters:stimTime")
		self.tailtime = self.parameters.get("edu.wisc.sinhalab.protocols.LedPulse:protocolParameters:tailTime")

		self.startdate = self.parameters["startDate"]
		self.enddate = self.parameters["endDate"]

	def __str__(self):
		return f"Epoch(cell_name={self.cellname}, start_date={self.startdate})"

	@property
	def values(self):
		path_to_response = self.responses['Amp1']["path"]
		data = self.h5file[path_to_response]['data'][:]

		return np.fromiter([x[0] for x in data], dtype=float)


from typing import Dict
from dataclasses import dataclass

import numpy as np

@dataclass
class SymphonyEpoch:

	path: str
	cellname: str
	startdate: float
	protocolname:str
	celltype:str
	tracetype:str
	enddate: float
	interpulseinterval:float
	led: str
	lightamplitude: float
	rstarr:float
	lightmean: float
	numberofaverages: float
	pretime: float
	stimtime: float
	samplerate: float
	tailtime: float
	responses: Dict



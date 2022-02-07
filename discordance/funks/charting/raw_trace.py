
from pathlib import Path
from typing import Union

import matplotlib.pyplot as plt

from ...epochtypes import SpikeTrace, WholeTrace

def plt_trace(epoch:Union[SpikeTrace, WholeTrace], outputfile:Path=None):
	fig, ax = plt.subplots()
	plt.plot(epoch.values)
	plt.title(epoch.startdate)
	plt.grid(True)

	plt.ylabel("pA")
	plt.xlabel("10e-4 seconds")

	if outputfile:
		plt.savefig(outputfile, dpi = 600)
	plt.show()
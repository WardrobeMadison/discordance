import itertools
from dataclasses import dataclass, field
from typing import Iterator, List, Tuple
from collections import defaultdict

import pandas as pd
import numpy as np

from . import baseepoch as bt 
from . import spikeepoch as st
from . import wholeepoch as wt

def groupby(traces: bt.EpochBlock, grpkeys) -> pd.DataFrame:
	"""
	Convert Traces to table with Epochs grouped by grpkeys
	"""
	grpd = defaultdict(list)
	epochtype =  type(traces[0]) # ASSUME SINGLE TYPE PER LIST

	if epochtype == wt.WholeEpoch: types = wt.WholeEpochs
	elif epochtype == st.SpikeEpoch: types = st.SpikeEpochs
	else: types = None

	for trace in traces.epochs:
		key = "___".join(map(str,(getattr(trace,arg) for arg in grpkeys)))
		grpd[key].append(trace)

	# CONVERT TRACE LIST TO TRACES
	data = []
	for key, grp in grpd.items():
		if len(grp) > 0:
			data.append([*key.split("___"), types(grp)])
	
	df = pd.DataFrame(columns = [*grpkeys, "trace"], data=data)

	return df

def filter(epochs, **kwargs):
	out = []
	for epoch in epochs:
		condition = all([
			getattr(epoch, key) == val
			for key, val in kwargs.items()
		])
		if condition: out.append(epoch)
	tracetype = type(epochs)
	return tracetype(out)





import itertools
from dataclasses import dataclass, field
from typing import Iterator, List, Tuple

import pandas as pd
import numpy as np

from . import baseepoch as bt 
from . import spikeepoch as st

def groupby(traces: bt.Epochs, grpkeys) -> pd.DataFrame:
	"""
	Convert Traces to table with Epochs grouped by grpkeys
	"""
	# ALWAYS PROCESS TYPE FIRST, MAKE THE OTHERS PLURAL
	args_traces = [x+"s" for x in grpkeys]

	# GET SET OF KEY VALUES TO FILTER LIST
	grpon = list()
	for arg in args_traces:
		vals = set(getattr(traces, arg))
		if len(vals):
			grpon.append(vals)
	
	# ALL COMBINATIONS OF KEY VALUES
	keys = list(itertools.product(*grpon))

	# FOR EACH GROUP BY KEY
	grpd = [list() for _ in range(len(keys))]
	# TODO pop items already in group out of list so you don't recheck
	for trace in traces.traces:
		for ii, key in enumerate(keys):
			# CHECK THAT TRACE MATCHES ALL KEY VALUES
			condition = all([
				getattr(trace, arg) == keyval
				for arg, keyval in zip(grpkeys,key)])
			if condition:
				grpd[ii].append(trace)
				break

	# CONVERT TRACE LIST TO SPIKETRACES
	data = []
	for key, grp in zip(keys, grpd):
		if len(grp) > 0:
			data.append([*key, st.SpikeEpochs(grp)])
	
	df = pd.DataFrame(columns = [*grpkeys, "trace"], data=data)

	return df

def filter(traces, **kwargs):
	out = []
	for trace in traces.traces:
		condition = all([
			getattr(trace, key) == val
			for key, val in kwargs.items()
		])
		if condition: out.append(trace)
	tracetype = type(traces)
	return tracetype(out)





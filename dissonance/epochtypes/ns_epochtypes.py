import itertools
from dataclasses import dataclass, field
from typing import Iterator, List, Tuple
from collections import defaultdict

import pandas as pd
import numpy as np

from . import baseepoch as bt 
from . import spikeepoch as st
from . import wholeepoch as wt
from . import sacaadeepoch as sa
from . import chirpepoch as ce

def groupby(frame:pd.DataFrame, grpkeys) -> pd.DataFrame:
	"""
	Convert Traces to table with Epochs grouped by grpkeys
	"""
	grpd = defaultdict(list)
	epochtype =  type(frame.epoch.iloc[0])# ASSUME SINGLE TYPE PER LIST

	if epochtype == wt.WholeEpoch: types = wt.WholeEpochs
	elif epochtype == st.SpikeEpoch: types = st.SpikeEpochs
	elif epochtype == sa.SaccadeEpoch: types = sa.SaccadeEpochs
	elif epochtype == ce.ChirpEpoch: types = ce.ChirpEpochs
	else: types = None

	data = []
	for key, grp in frame.groupby(grpkeys):
		data.append([*key, types(grp["epoch"].values)])

	
	return pd.DataFrame(columns = [*grpkeys, "epoch"], data=data)

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





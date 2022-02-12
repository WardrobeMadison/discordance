from typing import List, Tuple

import seaborn as sns

from .base import Tree
from ..epochtypes import groupby

class AnalysisTest(Tree):
	name = "AnalysisTest"
	labels = ("protocolname", "celltype", "cellname", "lightamplitude", "lightmean") 
	
	def __init__(self, epochs):
		self.groupedvals = groupby(epochs, self.labels)
		super().__init__(self.name, self.labels, self.groupedvals)

		# Specify which node gets what analysis
		# Group epochs at that level by traversing sub trees

	def psth(self, scope, epochs):
		...


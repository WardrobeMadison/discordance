from typing import List, Tuple, Dict, Any
from .node import Node

class Tree(Node):
	
	def __init__(self, name:str, labels: List[str], keys: List[Tuple]):
		"""Tree structure. Used in selecting data for analysis.

		Parameters
		----------
		name : str
			name of root node
		labels : List[str]
			labels to split tree on. Corresponds to order of keys.
		keys : List[Tuple]
			values to build tree from
		"""
		super().__init__("Name", name)
		self.keys = keys
		for key in keys:
			self.build_tree(key, self, labels)

	def build_tree(self, branch, node, labels):
		if len(branch) == 1:  # branch is a leaf
			cnode = Node(labels[0], branch[0])
			node.add(cnode)
		else:
			nodevalue, others = branch[0], branch[1:]
			label, olabels = labels[0], labels[1:]
			cnode = Node(label, nodevalue)
			if cnode not in node:
				node.add(cnode)
			else:
				cnode = node[nodevalue]
			self.build_tree(others, cnode, olabels)

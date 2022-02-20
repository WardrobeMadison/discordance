from typing import List, Tuple, Dict, Any
from .node import Node

class Tree(Node):
	
	def __init__(self, name, labels: List[str], keys: List[Tuple]):
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

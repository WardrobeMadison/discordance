
from pathlib import Path
from typing import List, Union
from dataclasses import dataclass, field
from typing import Iterator, Dict

class Node:
	def __init__(self, label, uid):
		self._parent = None
		self._path = None
		self.label = label
		self.uid = uid
		self.children = list()

	def __str__(self):
		return f"Node({self.label}={self.uid}, nchildren={len(self.children)})"

	@property
	def leaves(self):
		if self.isleaf: return self
		def _leaves(node):
			for child in node:
				if child.isleaf:
					yield child
				else: 
					yield from _leaves(child)
		for child in self.children:
			yield from _leaves(child)

	def __repr__(self):
		return f"Node({self.label}={self.uid}, nchildren={len(self.children)})"

	def __getitem__(self, val):
		if isinstance(val, str) or isinstance(val,float) or (val is None):
			idx = [child.uid for child in self.children].index(val)
			return self.children[idx]
		else:
			return self.children[val]

	@property
	def path(self) -> Dict[str, str]:
		if self.isroot:
			self._path = {self.label: self.uid}
		else:
			parpath = self._parent.path
			parpath[self.label] = self.uid
			self._path =  parpath
		return self._path

	@property
	def subpaths(self, rel=False) -> List[str]:
		return (leaf.path for leaf in self.leaves)

	def __iter__(self):
		for x in self.children:
			yield x

	def __eq__(self, othernode):
		return othernode.uid == self.uid

	def __neq__(self, othernode):
		return othernode.uid != self.uid

	def __contains__(self,val):
		return val in self.children

	@property
	def visual(self):
		self._prettify(self)

	def _prettify(self, tree, indent=1):
		'''
		Print the file tree structure with proper indentation.
		'''
		if tree.isleaf: print(tree); return

		if tree.isroot:
			print(tree)
		for node in tree:
			if node.isleaf:
				print('  ' * indent + str(node))
			else:
				print('  ' * indent + str(node))
				if not node.isleaf:
					self._prettify(node, indent+1)
				else:
					print('  ' * (indent+1) + str(node))

	@property
	def isroot(self):
		return self._parent is None

	@property
	def isleaf(self):
		return len(self.children) == 0

	@property
	def parent(self):
		return self._parent

	@parent.setter
	def parent(self, node):
		self._parent = node

	def add(self, node):
		for child in self:
			if child.uid == node.uid:
				child.children.extend(node.children)
				return
		node.parent = self
		self.children.append(node)

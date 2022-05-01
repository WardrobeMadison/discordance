
from datetime import datetime
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
		#idx = [child.uid for child in self.children].index(val)
		for child in self.children:
			if child.isleaf:
				if str(child.uid) == val:
					return child
			else: 
				if child.uid == val:
					return child

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
		return self._prettify(self)

	def _prettify(self, tree, indent=1):
		'''
		Print the file tree structure with proper indentation.
		'''
		visual = ""
		if tree.isleaf: visual = str(tree)

		if tree.isroot:
			visual += str(tree) + "\n"
		for node in tree:
			if node.isleaf:
				visual += '  ' * indent + str(node) +"\n"
			else:
				visual += '  ' * indent + str(node) + "\n"
				if not node.isleaf:
					visual += self._prettify(node, indent+1)
				else:
					visual += '  ' * (indent+1) + str(node) + "\n"
		return visual

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

	def traverse(self):
		if not self.isleaf:
			for x in self.children:
				yield x

			for x in self.children:
				yield from x.traverse()

	def select_node(self, **kwargs):
		if len(kwargs) < len(self.path):
			raise Exception("Can't traverse upwards. Start a higher node")
		#for node in self.traverse():
		#	if node.path == kwargs:
		#		return node
		node = self
		for ii, (key,val) in enumerate(kwargs.items()):
			if node.isleaf:
				return node
			if ii != 0:
				node = node[val]
		return node
		


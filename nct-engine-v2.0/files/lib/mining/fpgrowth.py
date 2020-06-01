'''
 FP-growth algorithm to mine frequent itemsets from a data collection

 @author: Riccardo Miotto <rm3086 (at) columbia (dot) edu
'''

# @param data = [(id_doc, [items])]
from lib.utility.log import strd_logger
import argparse, sys

log = strd_logger ('arule-mining')

def fpgrowth (data, minsup):
	itr = _frequent_pattern_generator (data, minsup)
	itemsets = {}

	for it in itr:
		
		pit = tuple(sorted(it[0]))
		itemsets[pit] = it[1]
		
	return itemsets


'''
 private functions
'''

# generate the frequent patterns
def _frequent_pattern_generator (data, minsup):
	fpt = FPTree.create_by_data (data, minsup)
	for fp in fpt.mine_frequent_patterns():
		yield fp


'''
 classes
'''

# frequent pattern tree
class FPTree(object):
		
	# constructor	
	def __init__ (self, minsup):
		self.min_support = minsup
		self.header_table = {}
		self.root = FPNode(None, None)
		self.item_sup = {}

	# check if the tree is empty  
	def is_empty (self):
		return len(self.root.children) == 0

	# mine the frequent patterns
	def mine_frequent_patterns(self):
		for fi in self.__fp_growth(tuple()):
			yield fi
	
	# static functions
	
	# create FP-tree from data organized as [(id_doc, [items])}
	@staticmethod
	def create_by_data(data, minsup):

		wdata = [(d[1],1) for d in data]

		return FPTree.create_by_weighted_data(wdata, minsup)
  
	# create FP-tree from data organized as [(item,w)]
	@staticmethod
	def create_by_weighted_data(wdata, minsup):
		self = FPTree(minsup)
		
		
		
		for items, weight in wdata:

			for item in set(items):
				self.item_sup[item] = self.item_sup.get(item,0) + weight
		# sort
  		freq_rev_list = sorted([(i,f) for (i,f) in self.item_sup.items() if f >= minsup], key=lambda(i,f):f, reverse=True)
		freq_rev_order = dict((i,o) for (o,(i,f)) in enumerate(freq_rev_list))
		# insert into the tree	
		for items, weight in wdata:
			freq_items = sorted([i for i in set(items) if i in freq_rev_order], key = lambda i:freq_rev_order[i])
			self.__insert(freq_items, weight)  
		return self

	# private functions
	  	
	# insert element in the tree
	def __insert(self, fitems, weight):
		cnode = self.root
		for item in fitems:
			if item not in cnode.children:
				nnode = FPNode(item, cnode)
				cnode.children[item] = nnode
				self.header_table.setdefault (item,[]).append(nnode)
			cnode = cnode.children[item]
			cnode.count += weight

	# fp-growth algorithm
	def __fp_growth(self, suffix):
		for item in self.header_table:
			nsfx = (item,) + suffix
			yield (nsfx, self.item_sup[item])
			cond_tree = self.__build_conditional_tree(item)
			if not cond_tree.is_empty():
				for fp in cond_tree.__fp_growth(nsfx):
					yield fp

	# get the conditional tree
	def __build_conditional_tree(self, item):
		cond_db = []
		for node in self.header_table[item]:
			path = []
			cnode = node.parent
			while cnode is not self.root:
				path.append(cnode.item)
				cnode = cnode.parent
			cond_db.append((path, node.count))
		return FPTree.create_by_weighted_data(cond_db, self.min_support)

	
# frequent pattern tree node
class FPNode(object):
	
	# constructor
	def __init__(self, item, parent):
		self.item = item
		self.count = 0
		self.children = {}
		self.parent = parent


  


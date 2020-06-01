'''
 Mining tag-based association rule in a collection of documents

 @author: Riccardo Miotto <rm3086 (at) columbia (dot) edu>
'''

from fpgrowth import fpgrowth
import math, random
from lib.utility.log import strd_logger
import argparse, sys

log = strd_logger ('arule-mining')

'''
 Mining the association rules using the fp-growth algorithm
 @param index: [(id_doc,[tags])]
 @param minsup: minimum support (probability)
 @param minconf: minimum confidence (probability)
'''
def mining (index, minsup = 0.01, minconf = 0.2):
	nminsup = math.ceil (minsup * len(index))
	
	# mine frequent itemsets
	itemsets = fpgrowth (index, nminsup)
	
	# derive the rules
	return _derive_association_rule (itemsets, minconf)



# private functions

'''
 Derive the association rules from the frequent itemsets
 @output rule: {<(items),[antecedent items sorted by confidence]>}
'''
def _derive_association_rule (itemsets, minconf):
	rule = {}
	for it in itemsets:

		if len(it) > 1:
			items = set(it)
			supp = itemsets[it]
			for sright in items:
				sleft = tuple(sorted(items - set([sright])))
				conf = supp / float(itemsets[tuple([sright])])
				if (conf >= minconf):
					cons = rule.setdefault (sleft, {})
					cons[sright] = conf
					rule[sleft] = cons
	# sort the right-sides by confidence
	for ru in rule.keys():
		cons = [(key,val) for (key,val) in reversed(sorted(rule[ru].iteritems(), key=lambda (k,v): (v,k)))]
		rule[ru] = cons
	return rule


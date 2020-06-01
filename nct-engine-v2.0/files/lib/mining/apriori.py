# implementation of the Apriori algorith to mine association rules

# @author: rm3086@columbia.edu

# @param data: list of tuple, each tuple has an 'id' and a list of items ([(tid, [item1, ...]), ...])
# @param minSupport: minimum support
def apriori(data, min_support): 	

	# get item frequencies
	freq = {}
	for tid, items in data:
		for item in set(items):
			freq[item] = freq.get(item,0)+1
  	
	# get frequent items and 1-item frequent itemsets
	result = {}
	freq_items = dict((k,v) for k,v in freq.items() if v >= min_support)
	sdata = [(tid,set(i for i in items if i in freq_items)) for tid,items in data]
	freq_itemsets = dict(((i,), f) for (i,f) in freq_items.iteritems())
	result[1] = freq_itemsets
  	
	# iterate all over the combinations
	for curr_itemset_size in xrange(2,len(freq_items)+1):
		
		# get the new itemsets
		joined_itemsets = [_join_itemsets(s1,s2) 
							for s1 in freq_itemsets 
								for s2 in freq_itemsets 
									if _joinable_itemsets(s1,s2)]
  		
		# prune the itemsets
		pruned_itemsets = [iset for iset in joined_itemsets 
									if all(sub_iset in freq_itemsets for sub_iset in _minus_one_subset(iset))]
  		
		# get frequencies
		item_set_freqs = dict((itemset,0) for itemset in pruned_itemsets)
		for tid,items in sdata:
			for itemset in pruned_itemsets:
				if all(item in items for item in itemset):
					item_set_freqs[itemset]+=1
  		
		# update
		new_freq_itemsets = dict((k,v) for (k,v) in item_set_freqs.iteritems() if v >= min_support)
		if len(new_freq_itemsets)==0:
			break
		result[curr_itemset_size] = new_freq_itemsets
		freq_itemsets = new_freq_itemsets
  	
	# return all the frequent itemsets
	return result


# private functions  
def _joinable_itemsets(s1,s2):
	return all(x1 == x2 for x1,x2 in zip(s1,s2)[:-1]) and s1[-1] < s2[-1]
  
def _join_itemsets(s1,s2):
	return s1+s2[-1:]
  
def _minus_one_subset(s):
	for i in xrange(len(s)):
		yield s[:i]+s[i+1:]



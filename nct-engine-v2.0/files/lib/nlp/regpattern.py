# set of utilities to search for regular patterns in text

# @author: rm3086 (at) columbia (dot) edu

import re


# look for a regular expression in the text
def search_regular_pattern (txt, pttrn):
	re.purge ()
	re_arg = re.findall (pttrn, txt, re.S)
	if re_arg is None:
		return None
	rp = []
	for a in re_arg:
		rp.append (a)
	return rp


# return the index of a single pattern
def get_index_pattern (txt, pttrn):
	re_pttrn = re.search (pttrn, txt, re.S)
	ipttrn = None
	if re_pttrn:
		ipttrn = re_pttrn.span()
	return ipttrn

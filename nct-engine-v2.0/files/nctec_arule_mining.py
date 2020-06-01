'''
 Mine tag association rules from a controlled vocabulary-based index of eligibility criteria

 @algorithm: fp-growth algorithm

 @author: Riccardo Miotto <rm3086 (at) columbia (dot) edu>
 '''

import lib.utility.file as ufile
import lib.mining.arule as arule
from lib.utility.log import strd_logger
import argparse, sys

log = strd_logger ('arule-mining')


def arule_mining (index, msup = 0.01, mconf = 0.2, dout = None):
	log.info ('mining tag association rules')
	log.info (' --- processing index composed of %d items' % len(index))

	# format index to remove prefixes from tags
	cindex = _format_index (index)
	
	# mining
	rule = arule.mining (cindex, msup, mconf)
	
	# rule count
	rcont = 0
	for r in rule:
		rcont += len(rule[r])
	log.info (' --- mined %d different rules' % rcont)

	# saving
	if not ufile.mkdir (dout):
		log.error ('impossible to create the output directory -- not saving')
	elif ufile.write_obj ('%s/tags-arule.pkl' % dout, rule):
		log.info ('tag association rules saved in: %s' % dout)
	else:
		log.error ('impossible to save the association rule file')
	return rule


# private functions

# format index as [(id, [tags])]
def _format_index (index):
	cindex = []
	for d in index:
		tags = []
		for t in index[d]:
			if _check_tag(t):
				ft = _format_tag(t)
				if ft is not None:
					tags.append (ft)
		if len(tags) > 0:
			cindex.append ((d,tags))
	return cindex


# remove tags without prefix
def _format_tag (tag):
	if max(0,tag.find(':')+1) == 0:
		return None
	return tag


# skip tags
def _check_tag (tag):
	if ' age = ' in tag:
		return False
	if tag.endswith(' gender'):
		return False
	if (tag == 'male') or (tag == 'female'):
		return False
	return True




############################### 
#
# main function
#
###############################

# processing the command line options
def _process_args():
	parser = argparse.ArgumentParser(description='Tag-based Index - Association Rule Mining')
	parser.add_argument(dest='findex', help='document index filename')
	# output directory
	parser.add_argument('-o', default='./output', help='output directory (default: "./output")')	
	# minimum support
	parser.add_argument('-s', default='0.01', type=float, help='minimum support (default: 0.01)')
	# minimum confidence
	parser.add_argument('-c', default='0.2', type=float, help='minimum confidence (default: 0.2)')
	return parser.parse_args(sys.argv[1:])

	
if __name__ == '__main__' :
	# param
	args = _process_args()
	# load index
	index = ufile.read_obj (args.findex)
	
	if not index:
		log.error ('impossible to load the tag-based index - interrupting')
	else:
		
		arule_mining (index, args.s, args.c, args.o)
		
	print ''
	log.info ('task completed\n')

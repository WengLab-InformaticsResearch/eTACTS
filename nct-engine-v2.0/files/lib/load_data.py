'''
 Load supporting data (umsl, stop words, negrule, pos-tags

 @author: Riccardo Miotto <rm3086 (at) columbia (dot) edu>
'''

from .utility.log import strd_logger
from .nlp.stemming.umls import UmlsDictionary
from .utility import file
ufile = file
log = strd_logger ('load-data')


# load stop words
def load_stop_words (dstop):
	if not dstop:
		return None
	eng = ufile.read_file ('%senglish.csv' % dstop, 2)
	if not eng:
		eng = set()
	med = ufile.read_file ('%smedical.csv' % dstop, 2)
	if not med:
		med = set()
	pmed = set()
	for m in med:
		pmed.add (m + 's')
	med |= pmed
	stop = (eng,med)
	log.info ('loaded %d stopping words' % (len(eng) + len(med)))
	return stop


# load umls dictionary
def load_umls (dumls):
	if not dumls:
		return None
	umls = UmlsDictionary (dumls) 
	log.info ('UMLS data: %d dictionary pairs, %d semantic types' % (len(umls.norm), len(umls.stype)))
	return umls


# load part-of-speech tags
def load_pos_tags (fptag):
	if not fptag:
		return None
	ptag = ufile.read_file (fptag, 2)
	if not ptag:
		return None
	log.info ('loaded %d admitted sentence semantic tags' % len(ptag))
	return ptag


# load negation rules
def load_negation_rule (fnegrule):
	if not fnegrule:
		return None
	negrule = ufile.read_file (fnegrule)
	if not negrule:
		return None
	log.info ('loaded %d negation rules' % len(negrule))
	return negrule


# load all supporting files <stop_words, umls, pos-tags, negrule>
def load_data (dstop, dumls, fptag, fnegrule):
	stop = load_stop_words (dstop)
	umls = load_umls (dumls)
	ptag = load_pos_tags (fptag)
	negrule = load_negation_rule (fnegrule)
	return (stop, umls, ptag, negrule)

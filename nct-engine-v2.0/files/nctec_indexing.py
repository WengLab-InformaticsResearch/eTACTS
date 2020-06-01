'''
 Index eligibility criteria from ClinicalTrials.gov uisng the controlled vocabulary of frequen tags

 @author: Riccardo Miotto <rm3086 (at) columbia (dot) edu>
'''

from lib.ecindex.indexer import indexer
from lib.ecindex import ctgov
from lib.load_data import load_data
from lib.utility.log import strd_logger
import lib.utility.file as ufile
import argparse, sys
import pickle

log = strd_logger ('ctec-tag-mining')


def nctec_indexing (cvocab, dout = './output', ngr = 5, stop = None, umls = None, negrule = None, nprocs = 1):
	if not cvocab:
		log.error ('controlled vocabulary not found - interrupting')
		return
	log.info ('index the eligibility criteria in ClinicalTrials.gov using a controlled vocabulary')
	log.info (' --- using n-grams composed by at most %d words' % ngr)
	log.info (' --- using %d tags' % len(cvocab))

	# load pre-existing data
	nct_ec = ufile.read_obj ('nctec-indexin.pkl')
	if nct_ec is None:
		nct_ec = {}

	# get the list of clinical trials
	log.info ('downloading the list of clinical trials')
	lnct = ctgov.get_clinical_trials()

	if len(lnct) == 0:
		log.error (' --- not found any clinical trials - interrupting')
		return
	log.info (' --- found %d clinical trials ' % len(lnct))

	# get eligibility criteria
	toprocess = set(lnct) - set(nct_ec.keys())
	log.info ('downloading the eligibility criteria for %d trials' % len(toprocess))
	
	# file=open('trial_dict.pkl', 'rb')
	# p_t=pickle.load(file)
	# file.close()

	for nct in toprocess:
		ec = ctgov.get_ecriteria(nct)
		#ec = p_t[nct]
		if (len(ec[0]) > 0) or (ec[1] is not None):
			nct_ec[nct] = ec
	if len(nct_ec) == 0:
		log.error ('not found any eligibility criteria - interrupting')
		return


	ufile.write_obj ('nctec-indexing.pkl', nct_ec)
		
	log.info ('found eligibility criteria for %d clinical trials' % len(nct_ec))
	
	# indexing
	pdocs = indexer (nct_ec, cvocab, ngr, stop, umls, negrule, nprocs)
	
	# save
 	if dout:
		fout = '%s/nctec-cindex.pkl' % dout
		log.info ('index saved in: %s' % fout)
		if ufile.write_obj(fout,pdocs) is False:
			log.error (' --- impossible to save the index')

	return pdocs



############################### 
#
# main function
#
###############################

# processing the command line options
def _process_args():
	parser = argparse.ArgumentParser(description='Index Eligiblity Criteria by Tags in ClinicalTrials.gov')
	parser.add_argument(dest='fvocab', help='file containing the controlled vocabulary of tags')
	# output directory
	parser.add_argument('-o', default='./output', help='output directory (default: "./output")')	
	# max length of the n-grams
	parser.add_argument('-g', default=5, type=int, help='n-gram max length (default = 6)')
	# stop word file
	parser.add_argument('-w', default=None, help='stop word directory (default: None)')
	# umls directory
	parser.add_argument('-u', default=None, help='umls directory (default: None)')
	# negation rules
	parser.add_argument('-r', default=None, help='negation rule file (default: None)')
	# number of processers to use
	parser.add_argument('-c', default=1, type=int, help='number of processors (default: 1)')
	return parser.parse_args(sys.argv[1:])

	
if __name__ == '__main__' :
	# param
	args = _process_args()
	# load data
	tags = ufile.read_csv (args.fvocab)
	log.info ('loaded %d eligibility tags' % len(tags))
	cvocab = set()
	for t in tags:
		cvocab.add (t[0])
	(stop, umls, ptag, negrule) = load_data (args.w, args.u, None, args.r)
	# exec
	nctec_indexing (cvocab, args.o, args.g, stop, umls, negrule, args.c)
	print ''
	log.info ('task completed\n')
		



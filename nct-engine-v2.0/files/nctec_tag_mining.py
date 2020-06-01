'''
 Controlled vocabulary (tag) mining from eligibility criteria in ClinicalTrials.gov

 @author: Riccardo Miotto <rm3086 (at) columbia (dot) edu>
 '''

import lib.utility.file as ufile
from lib.cvocab.tagminer import tag_miner
from lib.ecindex import ctgov
from lib.utility.log import strd_logger
from lib.load_data import load_data
import random, argparse, sys
import pickle

log = strd_logger ('ctec-tag-mining')


def nctec_tag_mining (dout = './output', freq = 0.01, ntrial = 0, ngr = 5, stop = None, umls = None, ptag = None, nprocs = 1):
	log.info ('mine the controlled vocabulary of tags for eligibility criteria in ClinicalTrials.gov')
	log.info (' --- using n-grams composed by at most %d words' % ngr)
	log.info (' --- tag frequency bound = %.3f' % freq)

	# load pre-existing data
	nct_ec = ufile.read_obj ('nctec-mining.pkl')

	# compute new data
	if not nct_ec:
		# get the list of clinical trials
		log.info ('downloading the list of clinical trials')
		lnct = ctgov.get_clinical_trials()

		if len(lnct) == 0:
			log.error (' --- not found any clinical trials - interrupting')
			return
		log.info (' --- found %d clinical trials ' % len(lnct))
	
		# sub-sample the list of trials
		if (ntrial > 0) and (ntrial < len(lnct)):
			random.shuffle(lnct)
			lnct = set([ct for ct in lnct[:ntrial]])

		# get the eligibility criteria
		log.info ('downloading the eligibility criteria for %d trials' % len(lnct))
		nct_ec = {}
		
		# file=open('trial_dict.pkl', 'rb')
		# p_t=pickle.load(file)
		# file.close()

		for nct in lnct:
			ec = ctgov.get_ecriteria (nct)
			#ec= p_t[nct]
			if ec[1] is not None:
				nct_ec[nct] = ec[1]
			if len(nct_ec) == 0:
				log.error ('not found any eligibility criteria - interrupting')
				return
		ufile.write_obj ('nctec-mining.pkl', nct_ec)
		
	log.info ('found eligibility criteria for %d clinical trials' % len(nct_ec))

	# tag mining
	cvocab = tag_miner (nct_ec, freq, ngr, stop, umls, ptag, nprocs)
	if cvocab is None:
		log.error ('unable to extract the controlled vocabulary - interrupting')

	# save
	if not ufile.mkdir (dout):
		log.error (' --- impossible to create the output directory - not saving')
	else:
		sfreq = str(freq * 10).replace('.','')
		fout = '%s/cvocab-%s.csv' % (dout, sfreq)
		ocvocab = _format_cvocab (cvocab)
		log.info ('tags saved in: %s' % fout)
		if ufile.write_csv(fout,ocvocab) is False:
			log.error (' --- impossible to save the controlled vocabulary')
	return cvocab



### private functions ###

# format cvocab for saving
def _format_cvocab (cvocab):
	ocvocab = []
	for t in sorted(cvocab.keys()):
		ocvocab.append ([t, cvocab[t]])
	return ocvocab



############################### 
#
# main function
#
###############################

# processing the command line options
def _process_args():
	parser = argparse.ArgumentParser(description='Tag Mining from Eligibility Criteria in ClinicalTrials.gov')
	# no. of trials 
	parser.add_argument('-n', default=0, type=int, help='no. of trials for tag mining (default: 0 -- all)')
	# output directory
	parser.add_argument('-o', default='./output', help='output directory (default: "./output")')	
	# max length of the n-grams
	parser.add_argument('-g', default=5, type=int, help='n-gram max length (default = 6)')
	# threshold to consider a tag as frequent
	parser.add_argument('-b', default=0.02, type=float, help='frequent tag min frequency (probability; default: 0.02)')
	# stop word file
	parser.add_argument('-w', default=None, help='stop word directory (default: None)')
	# umls directory
	parser.add_argument('-u', default=None, help='umls directory (default: None)')
	# pos tags
	parser.add_argument('-p', default=None, help='part-of-speech admitted tag file (default: None)')
	# number of processers to use
	parser.add_argument('-c', default=1, type=int, help='number of processors (default: 1)')
	return parser.parse_args(sys.argv[1:])

	
if __name__ == '__main__' :
	# param
	args = _process_args()
	# load parameters
	(stop, umls, ptag, negrule) = load_data (args.w, args.u, args.p, None)
	print ('')
	nctec_tag_mining (args.o, args.b, args.n, args.g, stop, umls, ptag, args.c)

	print ('')
	log.info ('task completed\n')
		



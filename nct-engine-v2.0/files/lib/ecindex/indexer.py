'''
 Index a collection of clinical trial eligiblity criteria using the frequent tags (controlled vocabulary)
 
 @author: Riccardo Miotto <rm3086 (at) columbia (dot) edu>
'''

from lib.cvocab.textprocesser import TextProcesser
from lib.cvocab.cvalue import substring_filtering
from multiprocessing import Process, Queue
from lib.utility.log import strd_logger
import math, re

log = strd_logger('ec-indexer')


def indexer (docs, cvocab, ngr = 5, stop = None, umls = None, rneg = None, nprocs = 1):
	# worker
	def worker (docs, ldoc, cvocab, ngr, stop, umls, rneg, qout, p):
		ptxt = {} 
		i = 1
		cdiv = 0
		for d in ldoc:
			if i % 500 == 0:
				log.info (' --- core %d: processed %d documents' % (p,i))
			i += 1
			if docs[d][1] is not None:
				(pec, c) = _index_ec (docs[d][1], cvocab, ngr, stop, umls, rneg)
				ptxt[d] = docs[d][0] | pec
				cdiv += c
		qout.put ((ptxt, cdiv))
	
	# chunksize each process with a queue to store results
	qout =  Queue()
	procs = []
	chunksize = int(math.ceil(len(docs) / float(nprocs)))
	ldoc = sorted(docs.keys())
	for i in range(nprocs):
		p = Process(target=worker, args=(docs, ldoc[chunksize*i:chunksize*(i+1)], cvocab, ngr, stop, umls, rneg, qout, (i+1)))
		procs.append(p)
		p.start()
	
	#  collect all results into a single result dict
	pdocs = {}
	cdiv = 0
	for i in range(nprocs):
		item = qout.get()
		pdocs.update (item[0])
		cdiv += item[1]
	
	# wait for all worker processes to finish
	for p in procs:
		p.join()

        # stats
        log.info ('processed %d documents' % len(pdocs))
	log.info (' --- obtained %d trials with reported inclusion/exclusion' % cdiv)
        icont = 0
        for d in pdocs:
            if len(pdocs[d]) > 0:
		    icont += 1
        log.info (' --- obtained %d documents with tags' % icont)
	return pdocs



# private functions

# extract tags from the eligibility criteria
def _index_ec (ec, cvocab, ngr, stop, umls, rneg):
	ptxt = ' '.join(ec.replace('\n',' ').split())
	pec = _preprocess_ec (ptxt)
	cdiv = 0
	if ('inc' in pec.keys()) or ('exc' in pec.keys()):
		cdiv = 1
	ectags = set ()
	for typ in pec:
		sent = pec[typ].split(' - ')
		ttag = {}
		for s in sent:
			proc = TextProcesser (s, ngr, stop, umls, None, rneg, cvocab)
			proc.process ()
			for pp in proc.ptxt:
				freq = ttag.setdefault(pp, 0)
				ttag[pp] = freq + 1
		if len(ttag) == 0:
			continue
		ttag = substring_filtering (ttag,1)
		for t in ttag:
			if typ == 'notyp':
				if t.startswith('^'):
					t = t[1:]
				ectags.add (t)
			else:
				if not t.startswith('^'):
					ectags.add ('%s:%s' % (typ,t))
				else:
					if typ == 'inc':
						ectags.add ('exc:%s' % t[1:])
					elif typ == 'exc':
						ectags.add ('inc:%s' % t[1:])
	return (ectags, cdiv)
				
		

# pre-process eligiblity criteria to guess inclusion/exclusion
def _preprocess_ec (ec):
	stype = {}
	try:
		ec = ec.lower().strip()
		# get inclusion
		re_inc = re.search (r'(inclusion\s*criteria(.*?)(?=[:;\s]){1})', ec, re.S)
		iinc = None
		if re_inc:
			iinc = re_inc.span()
		# get exclusion
		re_exc = re.search (r'(exclusion\s*criteria(.*?)(?=[:;\s]){1})', ec, re.S)
		iexc = None
		if re_exc:
			iexc = re_exc.span()
		if iinc and iexc:
			if iinc[0] < iexc[0]:
				stype['inc'] = ec[iinc[1]+1:iexc[0]-1].strip()
				stype['exc'] = ec[iexc[1]+1:].strip()
			else:
				stype['exc'] = ec[iexc[1]+1:iinc[0]-1].strip()
				stype['inc'] = ec[iinc[1]+1:].strip()
		elif iinc and (iexc is None):
			stype['inc'] = ec[iinc[1]+1:].strip()
		elif (iinc is None) and iexc:
			stype['exc'] = ec[iexc[1]+1:].strip()
		else:
			stype['notyp'] = ec.strip()
		return stype
	except Exception as e:
		log.error (e)
		return None




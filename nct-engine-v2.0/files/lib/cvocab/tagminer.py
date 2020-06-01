'''
 Mine a controlled vocabulary of tags from a collection of documents

  @author: Riccardo Miotto <rm3086 (at) columbia (dot) edu>
'''
from .textprocesser import TextProcesser
import math, numpy

from .cvalue import substring_filtering
from multiprocessing import Process, Queue
from lib.utility.log import strd_logger

log = strd_logger('tag-miner')


def tag_miner (docs, freq = 0.01, ngr = 5, stop = None, umls = None, ptag = None, nprocs = 1):
	# worker
	def worker (docs, ldoc, ngr, stop, umls, ptag, qout, p):
		ptxt = {}
		idf = {}
		i = 1
		for d in ldoc:
			if i % 500 == 0:
				log.info (' --- core %d: processed %d documents' % (p,i))
			i += 1
			pdoc = _parse_text (docs[d], ngr, stop, umls, ptag)
			if not pdoc:
				continue
			ptxt[d] = pdoc
			for t in ptxt[d]:
				val = idf.setdefault (t,0)
				idf[t] = val + 1
		qout.put ((ptxt, idf))
	
	# chunksize each process with a queue to store results
	qout =  Queue()
	procs = []
	chunksize = int(math.ceil(len(docs) / float(nprocs)))
	ldoc = sorted(docs.keys())
	for i in range(nprocs):
		p = Process(target=worker, args=(docs, ldoc[chunksize*i:chunksize*(i+1)], ngr, stop, umls, ptag, qout, (i+1)))
		procs.append(p)
		p.start()
	
	#  collect all results into a single result dict
	pdocs = {}
	idf = {}
	for i in range(nprocs):
		pdata = qout.get()
		pdocs.update (pdata[0])
		for t in pdata[1]:
			val = idf.setdefault(t,0)
			idf[t] = val + pdata[1][t]
	
	# wait for all worker processes to finish
	for p in procs:
		p.join()
	
	# compute idf
	for t in idf:
		idf[t] = math.log (len(pdocs) / float(idf[t]))
	
	# filter tags by tfidf analysis
	pdocs = _tfidf_analysis (pdocs, idf)

	# mine vocab
	cvocab = _mine_cvocab (pdocs, freq, idf, umls)
	log.info ('retained a controlled vocabulary of %d tags' % len(cvocab))
	return _add_semantic_types (cvocab, umls)



# private functions

# get the tag semantic types
def _add_semantic_types (cvocab, umls):
	ecvocab = {}
	for t in cvocab:
		stype = []
		if (umls is not None) and (t in umls.semantic):
			stype = sorted(umls.semantic[t] & umls.stype)
		ecvocab[t] = stype
	return ecvocab


# remove general tags in the documents
def _tfidf_analysis (pdocs, idf):
	for d in pdocs:
		if len(pdocs[d]) < 10:
			continue
		for t in pdocs[d]:
			pdocs[d][t] *= idf[t]
		freq = numpy.array(pdocs[d].values())
		th = freq.mean() - freq.std()
		for t in pdocs[d].keys():
			if pdocs[d][t] < th:
				del pdocs[d][t]
	return pdocs			
	

# extract tags from the text
def _parse_text (text, ngr, stop, umls, ptag):
	ptxt = ' '.join(text.replace('\n',' ').split())
	sent = ptxt.split(' - ')
	tags = {}
	for s in sent:
		proc = TextProcesser(s, ngr, stop, umls, ptag)
		proc.process ()
		for pp in proc.ptxt:
			freq = tags.setdefault(pp, 0)
			tags[pp] = freq + 1
	if len(tags) == 0:
		return 
	return substring_filtering (tags,1)


# mine the controlled vocabulary
def _mine_cvocab (pdocs, freq, idf, umls):
	cvocab = {}
	for d in pdocs:
		for t in pdocs[d]:
			val = cvocab.setdefault(t,0)
			cvocab[t] = val + 1
	log.info (' --- obtained %d n-grams' % len(cvocab))
	# retain the most frequent tags
	fth = math.ceil (freq * len(pdocs))
	for t in cvocab.keys():
		if cvocab[t] < fth:
			del cvocab[t]
	log.info (' --- retained %d tags appearing at least %d times' % (len(cvocab), fth))
	# clean the tags
	vidf = numpy.empty(len(cvocab))
	i = 0
	for t in cvocab:
		vidf[i] = idf[t]
		i += 1
	th = vidf.mean() - (2.5 * vidf.std())
	for t in cvocab.keys():
		if idf[t] < th:
			del cvocab[t]
	cvocab = substring_filtering (cvocab,50)
	return sorted(cvocab.keys())

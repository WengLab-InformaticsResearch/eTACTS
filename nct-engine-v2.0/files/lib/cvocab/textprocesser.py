'''
 Extract relevant tags from a text

  @author: Riccardo Miotto <rm3086 (at) columbia (dot) edu>
'''

import nltk, string, itertools
from lib.nlp import negex

from lib.utility.log import strd_logger
log = strd_logger ('ctec-tag-mining')



conj = set (['and', 'or'])


class TextProcesser:

	# constructor
	def __init__(self, text, ngram = 5, stop = None, umls = None, ptag = None, negrule = None, avocab = None):
		try:
			self.text = str(text.lower().strip())
		except UnicodeEncodeError:
			self.text = str(text.lower().strip().encode('utf-8'))
		self.text = self.text.replace('- ',' ').replace(' -',' ')
		toremove = string.punctuation.replace('-','')
		prep = string.maketrans(toremove, ' ' * len(toremove))
		self.text = ' '.join(self.text.translate(prep).split()).strip()
 		# get filtering data
		self.ngr = ngram
		if not stop:
			self.stop = (set(),set())
		else:
			self.stop = stop
		self.umls = umls
		
		# part of speech tagging
		self.ptag = ptag
		self.tpos = []
		if self.ptag:
			self.tpos = nltk.pos_tag (nltk.word_tokenize(self.text))
		# negation rule
		self.negrule = negrule
		if self.negrule:
			self.negrule = negex.sortRules(negrule)
		# admitted tags
		self.avocab = avocab
		self.ptxt = set()
	

	# process the text
	def process (self):
		if len(self.text) > 0:
			self. __tag_extraction (self.text.split())



	# private functions

	# extract tags by ngram analysis
	def __tag_extraction (self, words):
		for i in xrange(len(words)):
			for j in xrange(i+1, min(len(words), i+self.ngr) + 1):
				# grammar validity
				if len(words[i:j]) == 1:
					if self.ptag and not self.__check_grammar(i):
						continue
				# mapping
				t = self.__map_ngram (words[i:j])
				if t is not None:
					self.ptxt.add (t)
				elif (len(words) > 1) and (len(conj & set(words[i:j])) > 0):
					# analyze inner patterns with conjunctions
					stag = self.__scramble_ngram(words[i:j])
					if len(stag) > 0:
						self.ptxt |= stag
		return

	
	# standardize text by umls dictionary and semantic type
	def __umls_mapping (self, w):
 		if self.umls:
 			if (w not in self.umls.norm) or (len(self.umls.norm[w]) > 5):
 				return None
 			us = None
 			cl = int(1000)
 			wmap = None
 			for pt in self.umls.norm[w]:
 				dpt = pt.decode('utf-8')
 				# retain same
 				if dpt == w:
 					wmap = w
 					break
 				# acronym
 				if len(self.umls.norm[w]) > 1:
 					tkn = dpt.split()
 					if len(tkn) == len(w):
 						init = set(w)
 						acr = len(tkn)
 						for t in tkn:
 							if t[0] in init:
 								acr -= 1
 						if acr == 0:
 							wmap = dpt
 							break
 				# retain shorter
 				if (len(dpt) < cl):
 					wmap = dpt
 					cl = len(dpt)
 			if (wmap not in self.umls.semantic) or (len(self.umls.semantic[wmap] & self.umls.stype) == 0):
 				return None
 			return wmap.encode('utf-8').strip()
 		else:
 			return w


	# check tag validity
	def __check_tags (self, tag):
		if tag is None:
			return False
		words = tag.split()
		if len(words) > self.ngr:
			return False
		if len(words) == 1:
			if self.__check_word(tag) is False:
				return False
		else:
			if (words[0].isdigit()) or (words[-1].isdigit()):
				return False
			if (words[0] in self.stop[0]) or (words[-1] in self.stop[0]):
				return False
			cstop = 0
			for w in words:
				if self.__check_word(w) is False:
					cstop += 1
			if cstop == len(words):
				return False
		return True
				
	
	# check word validity
	def __check_word (self, w):
		if w.isdigit():
			return False
		if len(w) == 1:
			return False
		if (w in self.stop[0]) or (w in self.stop[1]):
			return False
		return True
	
	
	# check word grammar validity
	def __check_grammar (self, iword):
		if self.tpos[iword][1] in self.ptag:
			return False
		return True
	
	
	# analyze scrambled ngrams
	def __scramble_ngram (self, words):
		stag = set()
		comb = set(itertools.permutations(words))
		for c in comb:
			if len(c) == 1:
				continue
			t = self.__map_ngram (c)
			if t is not None:
				stag.add (t)
		return stag


	# check negation of words in text
	def __check_negation (self, w):
		if not self.negrule:
			return False
		tagger = negex.negTagger (self.text, w, self.negrule, False)
		if tagger.getNegationFlag() == 'negated':
			return True
		return False


	# map the ngram to tag
	def __map_ngram (self, words):
		w = ' '.join(words).strip()
		if not self.__check_tags(w):
			return None
		t = self.__umls_mapping (w)
		if not self.__check_tags(t):
			return None
		# admitted tags
		if self.avocab and t not in self.avocab:
			return None
		if self.__check_negation (words):
			t = '^%s' % t
		return t
				

			
		

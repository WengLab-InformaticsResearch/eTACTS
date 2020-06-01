# class to store the umls maps

# @author: rm3086@columbia.edu

from lib.utility.file import read_file,read_csv

class UmlsDictionary:

	# constructor
	# @variable norm: map 'sentence' to 'preferred sentence'
	# @variable semantic: map 'preferred sentence' to 'semantic types'
	# @variable stype: list of semantic types 
	def __init__(self, dumls = None):
		if dumls is not None:
			if dumls.endswith('/') is False:
				dumls += '/'
			self.__load_from_file (dumls)
		else:
			self.norm = {}
			self.semantic = {}
			self.stype = set()


	# load umsl data from files stored in 'dumls'
	def __load_from_file (self,dumls):
		# load categories
		st = read_file (dumls + 'umls-semantic.csv', 2)
		if st is not None:
			self.stype = set([c.lower() for c in st])
		else:
			self.stype = set()
		# load dictionary
		self.norm = {}
		self.semantic = {}
		udct = read_csv (dumls + 'umls-dictionary.csv')
		if udct is not None:
			for u in udct:
				# semantic types
				stype = set (u[2].strip().split('|'))
				# preferred terms
				pterms = u[1].strip().split('|')
				ns = set ()
				for pt in pterms:
					ns.add (pt)
					sty = self.semantic.setdefault (pt, set())
					sty |= stype
					self.semantic[pt] = sty
				if len(ns) > 0:
					self.norm[u[0].strip()] = ns


	# set variables
	def set_normalizer (self,nm):
		self.norm = nm

	
	def set_semantic_map (self,smap):
		self.semantic_map = smap


	def set_semantic_type (self,stype):
		self.semantic_type = stype


	# retrieve the semantic type of a term
	def retrieve_semantic_category (self, c):
		if c in self.semantic:
			return sorted(self.semantic[c])
		return None
		




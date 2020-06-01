'''
 Function to Interact with ClinicalTrials.gov

 @author: Riccardo Miotto <rm3086 (at) columbia (dot) edu>
 '''

import re, math
from lib.utility.web import download_web_data
import xml.etree.ElementTree as pxml
from lib.utility.log import strd_logger
from xml.etree import ElementTree
import lib.utility.file as ufile


log = strd_logger ('arule-mining')

# list of all trials available
def get_clinical_trials ():
	'''
	url = 'http://clinicaltrials.gov/ct2/crawl'
	html = download_web_data (url)
	pages = re.findall (r'href="/ct2/crawl/(\d+)"', html)
	lnct = set()
	print (lnct)
	for p in pages:
		html = None
		while html is None:
			html = download_web_data ('%s/%s' % (url, p))
		ct = re.findall (r'href="/ct2/show/(NCT\d+)"', html)
		lnct |= set(ct)
	'''
	#COVID-19 special

	txt='COVID-19'
	url = 'https://clinicaltrials.gov/api/query/field_values?expr=%s&field=NCTId'% txt
	xmltree = ElementTree.fromstring (download_web_data(url))
	lnct=[id.text for id in xmltree.find('FieldValueList').findall("FieldValue")]

	return lnct


# eligibility criteria block
def get_ecriteria (nct):
	#nct= 'NCT00120003'

	url = 'http://clinicaltrials.gov/show/%s?displayxml=true' % nct
	try:
		txml = None
		while txml is None:
			txml = pxml.fromstring (download_web_data(url))
		ec = txml.find ('eligibility')
		details = set()
		# gender
		val = ec.find('gender')
		if val is not None:
			t = val.text.lower().strip()
			if ('both' not in t) and ('n/a' not in t):
				details.add ('gender = ' + t)
		# minimum age
		val = ec.find('minimum_age')
		if val is not None:
			t = val.text.lower().strip()
			amin = _check_age ('minimum age = ' + t)
			if amin:
				details.add (amin)
		# maximum age
		val = ec.find('maximum_age')
		if val is not None:
			t = val.text.lower().strip()
			amax = _check_age ('maximum age = ' + t)
			if amax:
				details.add (amax)
		# free-text criteria
		d = ec.find ('criteria')
		ectxt = d.find ('textblock')
		if ectxt is not None:
			ectxt = ectxt.text.encode('utf-8').strip()
		#log.info(details)

		return (details, ectxt)
	except Exception as e:
		return (set(), None)



# private functions

# check the age format
def _check_age (age):
	try:
		val = int(age[age.rfind(' '):].strip())
		return age
	except ValueError:
		if 'year' in age:
			return age[:age.rfind('y')].strip()
		if 'month' in age:
			return _format_age (age[:age.rfind('m')].strip(), float(12))
		if 'week' in age:
			return _format_age (age[:age.rfind('w')].strip(), float(52))
		if 'day' in age:
			return _format_age (age[:age.rfind('d')].strip(), float(365))
		return None
		

# format the age tag
def _format_age (age, div):
	val = int(age[age.rfind(' '):])
	if 'maximum' in age:
		return 'maximum age = %d' % math.ceil(val/div)
	if 'minimum' in age:
		return 'minimum age = %d' % math.floor(val/div)
	return None

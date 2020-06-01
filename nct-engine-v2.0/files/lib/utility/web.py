# set of general utilities to interact with the Web

# @author: rm3086 (at) columbia (dot) edu

import urllib, json
import logging

# logger
log = logging.info ('web')

# get the html source associated to a URL
def download_web_data (url):
    try:
        #req = urllib.request (url, headers={'User-Agent':' Mozilla/5.0'}) 
        con = urllib.urlopen(url)
        html = con.read()
        con.close()
        return html
    except Exception as e:
        # log.error ('%s: %s' % (e, url))
        return None

# get json data
def download_json_data (url):
    try:
        con = urllib.urlopen(url)
        data = con.read()
        con.close()
        return json.loads(data)
    except Exception as e:
        log.error ('%s: %s' % (e, url))
        return None


# clean the html source
def clean_html (html):
	if html is None:
		return None
	return ' '.join(html.replace('\n','').replace('\t','').split()).strip()


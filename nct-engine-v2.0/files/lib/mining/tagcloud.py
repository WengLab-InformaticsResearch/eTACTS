'''
 Tag cloud simulation based on association rule
 
 @author: Riccardo Miotto <rm3086 (at) columbia (dot) edu>
 '''

import random, math

def tagcloud (iidx, arule, seed = None, atag = None, ntag = 30):
    # random tag number
    nrand = int(math.floor (ntag/5))
    # seed not defined
    if (not seed) or (len(seed) == 0):
        return _no_seed_cloud (iidx, atag, ntag, nrand)
    # defined seed
    stag = _tags_by_frequency (iidx, atag)
    ltag = seed
    utag = set(seed)
    cloud = []
    while len(ltag) > 0:
        tp = tuple(sorted(ltag))
        if tp in arule:
            for t in arule[tp]:
                if (t[0] in utag) or (t[0] not in atag):
                    continue
                cloud.append ((t[0], t[1]*10*len(ltag)))
                utag.add (t[0])
        if len(cloud) >= ntag:
            if len(cloud) >= (ntag + nrand):
                return _random_tags (cloud, ntag, nrand)
            return cloud[:ntag]
        ltag.pop()
    for t in stag:
        if (t[0] in utag) or (t[0] not in atag):
            continue
        cloud.append ((t[0], t[1]))
    if len(cloud) >= ntag:
        if len(cloud) >= (ntag + nrand):
            return _random_tags (cloud, ntag, nrand)
        return cloud[:ntag]
    return cloud



# private functions

# list of tags sorted by normalized frequency
def _tags_by_frequency (iidx, atag):
    stag = {}
    sfreq = 0
    for t in iidx:
        if (atag is None) or (t in atag):
	    stag[t] = len(iidx[t])
            sfreq += len(iidx[t])    
    return [(k, v/float(sfreq)) for k,v in reversed(sorted(stag.iteritems(), key = lambda x:x[1]))]


# tag cloud if the seed is not defined
def _no_seed_cloud (iidx, atag, ntag, nrand):
    cloud = _tags_by_frequency (iidx, atag)
    if len(cloud) >= (ntag + nrand):
        return _random_tags (cloud, ntag, nrand)
    elif len(cloud) >= ntag:
        return cloud[:ntag]
    return cloud


# extract random tags for the cloud
def _random_tags (cloud, ntag, nrand):
    ind = int(math.floor (ntag/5)) * 4
    tfirst = cloud[:ind]
    tlast = cloud[ind:(ntag+nrand)]
    random.shuffle (tlast)
    rcloud = tfirst + tlast
    return rcloud[:ntag]

#! /bin/bash

clear

dhome="/Users/yingcheng_sun/Desktop/eTACTS"
ddata=$dhome/Tag_Generation/etacts-data/projects/nctec-tag-mining
findex=$ddata/nctec-cindex.pkl


python files/nctec_arule_mining.py $findex -s 0.01 -c 0.2 -o $ddata

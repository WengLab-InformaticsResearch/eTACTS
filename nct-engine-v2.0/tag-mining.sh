#! /bin/bash

clear

dhome="/Users/yingcheng_sun/Desktop/eTACTS"
ddata=$dhome/Tag_Generation/etacts-data

python files/nctec_tag_mining.py -n 0 -b 0.01 -g 5 -w $ddata/csv/stop-words/ -u $ddata/csv/umls/ -p $ddata/csv/treebank-tags.csv -o $ddata/projects/nctec-tag-mining -c 4

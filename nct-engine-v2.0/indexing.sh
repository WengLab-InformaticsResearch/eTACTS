#! /bin/bash

clear

dhome="/Users/yingcheng_sun/Desktop/eTACTS"
ddata=$dhome/Tag_Generation/etacts-data
dvocab=$ddata/projects/nctec-tag-mining

python files/nctec_indexing.py $dvocab/cvocab-01.csv -g 5 -w $ddata/csv/stop-words/ -u $ddata/csv/umls/ -r $ddata/csv/negation-rules.txt -o $dvocab -c 4

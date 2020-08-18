#!/bin/bash

SPLIT=test
infile=asr_output/nbest/pa_${SPLIT}/pa_${SPLIT}.ctm
outfile=asr_output/nbest/pa_${SPLIT}/pa_${SPLIT}_mapped.ctm
mapfile=data/acronyms.map

~/kaldi/egs/swbd/s5c/local/map_acronyms_ctm.py -i $infile -o $outfile -M $mapfile



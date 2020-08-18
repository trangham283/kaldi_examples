#!/bin/bash

#SPLIT=test
#outfile=/homes/ttmt001/transitory/asr_preps/asr_output/nbest/${SPLIT}_asr_sents.tags
#infile=/homes/ttmt001/transitory/asr_preps/asr_output/nbest/${SPLIT}_asr_sents.txt

infile=/homes/ttmt001/transitory/asr_preps/asr_output/temp/sample_in.txt
outfile=/homes/ttmt001/transitory/asr_preps/asr_output/temp/sample_out.txt
modelfile=/s0/ttmt001/stanford-postagger-2018-10-16/models/english-left3words-distsim.tagger
cd /s0/ttmt001/stanford-postagger-2018-10-16
java -mx300m -cp 'stanford-postagger.jar:' edu.stanford.nlp.tagger.maxent.MaxentTagger -model $modelfile -sentenceDelimiter newline -textFile $infile > $outfile

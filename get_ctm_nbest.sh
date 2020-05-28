#!/usr/bin/env bash
# Copyright Johns Hopkins University (Author: Daniel Povey) 2012.  Apache 2.0.

# This script produces CTM files from a decoding directory that has lattices                                                                         
# present. It does this for a range of language model weights; see also 
# get_ctm_fast.sh which does it for just one LM weight and also supports
# the word insertion penalty, and get_ctm_conf.sh which outputs CTM files
# with confidence scores.


use_segments=true # if we have a segments file, use it to convert
                  # the segments to be relative to the original files.
print_silence=false

echo "$0 $@"  # Print the command line for logging

[ -f ./path.sh ] && . ./path.sh
. parse_options.sh || exit 1;

if [ $# -ne 3 ]; then
  echo "Usage: $0 [options] <data-dir> <lang-dir|graph-dir> <decode-dir>"
  exit 1;
fi

data=$1
lang=$2 # Note: may be graph directory not lang directory, but has the necessary stuff copied.
dir=$3

model=$lang/../final.mdl # assume model one level up from decoding dir.


for f in $lang/words.txt $model $dir/lat.1.gz; do
  [ ! -f $f ] && echo "$0: expecting file $f to exist" && exit 1;
done

name1=`basename $data`; # e.g. eval2000
name2=`dirname $data`
name3=`basename $name2`
name=${name3}_${name1}

mkdir -p $dir/scoring/log
mkdir -p $dir/score_nbest

nj=$(cat $dir/num_jobs)

for n in $(seq $nj);
do
  lat=$dir/lat.$n.gz
  gunzip -c $lat | \
  lattice-to-nbest --lm-scale=10 --n=10 ark:- ark:- | \
  nbest-to-linear ark:- ark,t:$dir/transition-ids-${n}.ali \
    ark,t:-  \
    ark,t:$dir/lm-costs-${n}.txt ark,t:$dir/acoustic-costs-${n}.txt | \
  utils/int2sym.pl -f 2- $lang/words.txt > $dir/transcript-${n}.txt

  gunzip -c $lat | \
  lattice-to-nbest --lm-scale=10 --n=10 ark:- ark:- | \
  lattice-determinize-pruned ark:- ark:- | \
  lattice-align-words $lang/phones/word_boundary.int $model ark:- ark:- | \
  nbest-to-ctm --frame-shift=$frame_shift \
    --print-silence=$print_silence ark:- - | \
  utils/int2sym.pl -f 5 $lang/words.txt >>  $dir/score_nbest/$name.ctm 
done



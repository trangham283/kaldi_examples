#!/bin/bash

task=da
split=dev
datadir=/s0/ttmt001/utterances/$task/$split
outdir=$task/$split
mkdir -p $outdir

# make list of files to process
find $datadir -iname '*.wav' | sort > $outdir/wav.flist
sed -e 's?.*/??' -e 's?.wav??' $outdir/wav.flist | paste - $outdir/wav.flist > $outdir/wav.scp

awk '{print $1}' $outdir/wav.scp > $outdir/utt2spk 

# Then some vim magic in utt2spk:
# - copy over to second column: CTRL+V all (include the space too); then CTRL+P; then ESC
# - delete turn_id from second column: CTRL+V last 5 characters (stuff from _*); D


#!/bin/bash
awk '{print $1}' wav_feat.scp \
  | perl -ane '$_ =~ m:^(\S+)-([AB])$: || die "bad label $_";
               print "$1-$2 $1-$2\n"; ' \
  > utt2spk || exit 1;



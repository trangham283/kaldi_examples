#!/bin/bash

if [ ! -d "/s0/ttmt001" ]
then
    space_req s0
echo "Creating scratch space"
fi

# Based on run.sh and local/eval2000_data_prep.sh
maindir=.
outdir=/s0/ttmt001/swbd_features
feat=pitch
datadir=/g/ssli/data/swbdI/dist/swb1
pitchdir=$outdir/pitch
logdir=$maindir/log
swdir=$HOME/kaldi/src/featbin

nj=8
cmd=utils/run.pl
pitch_config=conf/pitch.conf
compress=true

# make list of files to process
find $datadir -iname '*.sph' | sort > sph.flist
sed -e 's?.*/??' -e 's?.sph??' sph.flist | paste - sph.flist > sph.scp

sph2pipe=$HOME/kaldi/tools/sph2pipe_v2.5/sph2pipe
[ ! -x $sph2pipe ] \
  && echo "Could not execute the sph2pipe program at $sph2pipe" && exit 1;

awk -v sph2pipe=$sph2pipe '{
  printf("%s-A %s -f wav -p -c 1 %s |\n", $1, sph2pipe, $2); 
  printf("%s-B %s -f wav -p -c 2 %s |\n", $1, sph2pipe, $2);
}' < sph.scp | sort > wav.scp || exit 1;
#side A - channel 1, side B - channel 2

awk '{print $1}' wav.scp \
  | perl -ane '$_ =~ m:^(\S+)-([AB])$: || die "bad label $_";
               print "$1-$2 $1 $2\n"; ' \
  > reco2file_and_channel || exit 1;

# use "name" as part of name of the archive.
name=`basename $datadir`

mkdir -p $pitchdir || exit 1;
mkdir -p $logdir || exit 1;

if [ -f $maindir/feats.scp ]; then
    mkdir -p $maindir/.backup
    echo "$0: moving $maindir/feats.scp to $maindir/.backup"
    mv $maindir/feats.scp $maindir/.backup
fi

cp wav.scp $maindir/
scp=$maindir/wav.scp
required="$scp $pitch_config"

for f in $required; do
    if [ ! -f $f ]; then
        echo "make_mfcc.sh: no such file $f"
        exit 1;
    fi
done

split_scps=""
for n in $(seq $nj); do
    split_scps="$split_scps $logdir/wav_${name}.$n.scp"
done

utils/split_scp.pl $scp $split_scps || exit 1;


# Use the ",t" modifier on the output to convert to .txt file
# copy-feats scp:feats.scp ark,t:-

## compute pitch feats here
$cmd JOB=1:$nj $logdir/make_pitch_${name}_${feat}.JOB.log \
$swdir/compute-kaldi-pitch-feats --verbose=2 --config=$pitch_config \
scp,p:$logdir/wav_${name}.JOB.scp ark:- \| \
$swdir/process-kaldi-pitch-feats ark:- ark:- \| \
$swdir/copy-feats --compress=$compress ark:- \
ark,scp:$pitchdir/raw_pitch_$name.JOB.ark,$pitchdir/raw_pitch_$name.JOB.scp \
|| exit 1;

$cmd JOB=1:$nj $logdir/copy_text_${name}_${feat}.JOB.log \
$swdir/copy-feats ark:$pitchdir/raw_pitch_$name.JOB.ark ark,t:$pitchdir/raw_pitch_$name.JOB.txt \
|| exit 1;

if [ -f $logdir/.error.$name ]; then
  echo "Error producing pitch features for $name:"
  tail $logdir/make_pitch_${name}.1.log
  exit 1;
fi

# concatenate the .scp files together.
for n in $(seq $nj); do
  cat $pitchdir/raw_pitch_$name.$n.scp || exit 1;
done > $maindir/feats.scp

#rm $logdir/wav_${name}.*.scp  2>/dev/null

echo "Succeeded creating features for $name"

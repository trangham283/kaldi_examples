#!/bin/bash

if [ ! -d "/s0/ttmt001" ]
then
    space_req s0
echo "Creating scratch space"
fi

# Based on run.sh and local/eval2000_data_prep.sh
maindir=.
feat=fbank
outdir=/s0/ttmt001/swbd_features
datadir=/g/ssli/data/swbdI/dist/swb1
logdir=$maindir/log
swdir=$HOME/kaldi/src/featbin
fbankdir=$outdir/fbank
logdir=$maindir/log

nj=8
cmd=utils/run.pl
fbank_config=conf/fbank.conf
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
}' < sph.scp | sort > wav_feat.scp || exit 1;
#side A - channel 1, side B - channel 2

awk '{print $1}' wav_feat.scp \
  | perl -ane '$_ =~ m:^(\S+)-([AB])$: || die "bad label $_";
               print "$1-$2 $1 $2\n"; ' \
  > reco2file_and_channel || exit 1;

# use "name" as part of name of the archive.
name=`basename $datadir`

mkdir -p $fbankdir || exit 1;
mkdir -p $logdir || exit 1;

if [ -f $maindir/feats.scp ]; then
    mkdir -p $maindir/.backup
    echo "$0: moving $maindir/feats.scp to $maindir/.backup"
    mv $maindir/feats.scp $maindir/.backup
fi

cp wav_feat.scp $maindir/
scp=$maindir/wav_feat.scp
required="$scp $fbank_config"

for f in $required; do
    if [ ! -f $f ]; then
        echo "make_fbank.sh: no such file $f"
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
## compute fbank (+energy) here
$cmd JOB=1:$nj $logdir/make_fbank_${name}.JOB.log \
$swdir/compute-fbank-feats --verbose=2 --config=$fbank_config \
scp,p:$logdir/wav_${name}.JOB.scp ark:- \| \
$swdir/copy-feats --compress=$compress ark:- \
ark,scp:$fbankdir/raw_fbank_$name.JOB.ark,$fbankdir/raw_fbank_$name.JOB.scp \
|| exit 1;

$cmd JOB=1:$nj $logdir/copy_text_${name}_${feat}.JOB.log \
$swdir/copy-feats ark:$fbankdir/raw_fbank_$name.JOB.ark ark,t:$fbankdir/raw_fbank_$name.JOB.txt \
|| exit 1;

if [ -f $logdir/.error.$name ]; then
  echo "Error producing fbank features for $name:"
  tail $logdir/make_fbank_${name}.1.log
  exit 1;
fi

# concatenate the .scp files together.
for n in $(seq $nj); do
  cat $fbankdir/raw_fbank_$name.$n.scp || exit 1;
done > $maindir/feats.scp


rm $logdir/wav_${name}.*.scp  2>/dev/null

echo "Succeeded creating features for $name"


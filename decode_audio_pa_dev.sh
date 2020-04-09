export KALDI_ROOT=/homes/ttmt001/kaldi
export PATH=$PWD/utils/:$KALDI_ROOT/tools/openfst/bin:$PWD:$PATH
[ ! -f $KALDI_ROOT/tools/config/common_path.sh ] && echo >&2 "The standard file $KALDI_ROOT/tools/config/common_path.sh is not present -> Exit!" && exit 1
. $KALDI_ROOT/tools/config/common_path.sh
export PATH=$KALDI_ROOT/tools/sctk/bin:$PATH
export LC_ALL=C

lang_dir=data/lang_chain
extractor_dir=exp/nnet3/extractor
nnet_dir=exp/chain/tdnn_7b
datadir=my_data/parse/dev
outdir=decode_out

#steps/online/nnet3/prepare_online_decoding.sh \
#    --mfcc-config conf/mfcc_hires.conf \
#    $lang_dir $extractor_dir $nnet_dir $outdir

lang_decode_dir=data/lang_pp_test 
model_dir=$outdir
graph_dir=$outdir/graph_pp

#utils/mkgraph.sh --self-loop-scale 1.0 \
#    $lang_decode_dir $model_dir $graph_dir

# Here you might need to do fstconvert for graph:
# make a backup first:

#cp $graph_dir/HCLG.fst $graph_dir/HCLG_bak.fst
#$KALDI_ROOT/tools/openfst/bin/fstconvert $graph_dir/HCLG_bak.fst \
#    $graph_dir/HCLG.fst

post_dec=10.0
steps/online/nnet3/decode.sh --nj 2 --acwt 1.0 --post-decode-acwt ${post_dec} \
    $graph_dir $datadir $outdir/out_pa_dev

# get time alignments
lang_dir=$graph_dir
decode_dir=$outdir/out_pa_dev
./get_ctm_all.sh $datadir $lang_dir $decode_dir


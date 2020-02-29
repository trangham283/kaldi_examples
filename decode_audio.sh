post_dec=1.0
data_dir=sample_data
decode_dir=exp/tdnn_7b_chain_online
lattice_dir=exp/tdnn_7b_chain_online
lang_dir=exp/tdnn_7b_chain_online/graph_pp
graph_dir=exp/tdnn_7b_chain_online/graph_pp
out_dir=sample_data/out
decoded_text=decoded.1.txt

steps/online/nnet3/prepare_online_decoding.sh \
    --mfcc-config conf/mfcc_hires.conf \
    data/lang_chain exp/nnet3/extractor \
    exp/chain/tdnn_7b exp/tdnn_7b_chain_online

utils/mkgraph.sh --self-loop-scale 1.0 \
    data/lang_pp_test exp/tdnn_7b_chain_online \
    exp/tdnn_7b_chain_online/graph_pp

# Here you might need to do fstconvert for graph:
# make a backup first:
cp $graph_dir/HCLG.fst $graph_dir/HCLG_bak.fst
$KALDI_ROOT/tools/openfst/bin/fstconvert $graph_dir/HCLG_bak.fst \
    $graph_dir/HCLG.fst

# decode to lattice
steps/online/nnet3/decode.sh --nj 1 --acwt 1.0 \
    --post-decode-acwt ${post_dec} \
    exp/tdnn_7b_chain_online/graph_pp \
    example exp/tdnn_7b_chain_online/out

# choose best path
lattice-best-path --acoustic-scale=0.1 "ark,t:${latd}/output.1.lat" "ark,t:${latd}/output.1.txt"

# convert numbers to actual words
utils/int2sym.pl -f 2- ${graph_dir}/words.txt < ${latd}/output.1.txt > $decoded_text

# get time alignments
lattice-best-path --acoustic-scale=0.1 "ark:${latd}/output.1.lat" "ark,t:|int2sym.pl -f 2- ${graph_dir}/words.txt > ${decoded_text}" ark:1.ali

./get_ctm_local.sh $data_dir $lang_dir $decode_dir $out_dir


# Split audio into separate channels and convert to .wav format
$KALDI_ROOT/tools/sph2pipe_v2.5/sph2pipe -f wav -p -c 1 sw02001.sph sw02001_A.wav
$KALDI_ROOT/tools/sph2pipe_v2.5/sph2pipe -f wav -p -c 2 sw02001.sph sw02001_B.wav

# Just save a small portion to sample file
sox sw02001_A.wav sw02001_A_0035.wav trim 0 00:35
sox sw02001_B.wav sw02001_B_0035.wav trim 0 00:35

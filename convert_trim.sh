# Split audio into separate channels and convert to .wav format
$KALDI_ROOT/tools/sph2pipe_v2.5/sph2pipe -f wav -p -c 1 sw02001.sph sw02001_A.wav
$KALDI_ROOT/tools/sph2pipe_v2.5/sph2pipe -f wav -p -c 2 sw02001.sph sw02001_B.wav

# Just save a small portion to sample file
# This writes to the portion of the audio starting from 0s, lasting 35s
sox sw02001_A.wav sw02001_A_0035.wav trim 0 00:35
sox sw02001_B.wav sw02001_B_0035.wav trim 0 00:35

# To get the portion of audio from 1.2s to 10s, for example, you can do
sox sw02001_A.wav sw02001_A_0035.wav trim 1.2 =10

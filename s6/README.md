# s6 recipe
Backup/copy of local $HOME/kaldi/egs/swbd/s6

## Steps
* Feature extraction
```
migrate --max-mem 16000 --max-cpu 8 --no-desktop "./comp_pitch.sh"
migrate --max-mem 16000 --max-cpu 8 --no-desktop "./comp_mfcc.sh"
migrate --max-mem 16000 --max-cpu 8 --no-desktop "./comp_fbank.sh"
```

This got put on bird030

* Post-process: `run_postprocess.sh`
* tar it: e.g. `tar -czvf pitch_json.tar.gz /s0/ttmt001/swbd_features/pitch/json`

## Output
* on: /g/ssli/data/CTS-English/swbd_align/acoustic_features_json
* full swbd data done (all steps above) in ~6 hours total, on 8 CPUs (bird030); mfcc and fbank features take longer than pitch

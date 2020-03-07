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
* tar it

## Output
* on: /g/ssli/data/CTS-English/swbd_align/acoustic_features_json
* full swbd data done in ~4 hours, on 8 CPUs (bird030)

# kaldi_examples
Sample codes and data to follow up on TIAL group meeting on 2/25.
WIP

## References
* [Official docs](http://kaldi-asr.org/doc/)
* [Slides from Group Meeting](https://docs.google.com/presentation/d/1v_uF-_fa2wCnTRvMeHgru8YgyfvXOjrrgtbv4bJZ2WQ/edit?usp=sharing)
* [Eleanor Chodroff's tutorial](https://eleanorchodroff.com/tutorial/kaldi/)
* [JHU Summer Workshop](https://www.clsp.jhu.edu/wp-content/uploads/sites/75/2019/06/jhu_ss_kaldi_tutorial.pdf)
* Random blogs I found helpful:
  * http://www.programmersought.com/tag/kaldi/ 
  * [Using a pretrained model](https://medium.com/@nithinraok_/decoding-an-audio-file-using-a-pre-trained-model-with-kaldi-c1d7d2fe3dc5)
  * [Using and extending the ASpIRE model](https://chrisearch.wordpress.com/2017/03/11/speech-recognition-using-kaldi-extending-and-using-the-aspire-model/)

## Common Setup/Quick Start
  * Install Kaldi
  * Create a directory for data and experiments
  * Copy `cmd.sh` and `path.sh` to this directory; this should be the same in any `kaldi/egs` recipes
  * Example audio files are in `sample_data`; the audio has to be in .wav formatand mono-channel. For an example of how to do this, see `convert_trim.sh`

## Feature Extraction
  * Make sure the configurations are correct in `/conf`. For example:
    * I changed `fbank.conf` to also extract total energy by setting `use-energy=true`
    * I changed `mfcc.conf` to ; according to the ASpiRE-related models, this gave better results in speech recognition
  * `comp_all.sh` has the sample script to extract fbank, mfcc, and pitch features. Comment out parts you don't need


## Decoding Using a Pretrained Model
  * Download a model from [kaldi models](http://kaldi-asr.org/models.html). For this example, I'm using the [ASpIRE chain model](http://kaldi-asr.org/models/m1), version with the precompiled HCLG
  * Untar it: `tar xvf 0001_aspire_chain_model_with_hclg.tar.bz2`
  * To this recipe, copy `cmd.sh` and `path.sh` if you haven't done so
  * Link common modules we'll be using (or copy all these here if you'll be editing the scripts in these directory):
    ```
    ln -s $KALDI_ROOT/egs/aspire/s5/steps .
    ln -s $KALDI_ROOT/egs/aspire/s5/utils .
    ln -s $KALDI_ROOT/egs/aspire/s5/conf .
    ln -s $KALDI_ROOT/egs/aspire/s5/local .
    ```
  * 

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
  * [Desh Raj's blog posts](https://desh2608.github.io/2019-05-21-chain/)
  * [ASR lecture notes from University of Edinburgh](http://www.inf.ed.ac.uk/teaching/courses/asr/lectures-2020.html)

## Common Setup/Quick Start
  * Install Kaldi
  * Create a directory for data and experiments
  * Copy `cmd.sh` and `path.sh` to this directory; this should be the same in any `kaldi/egs` recipes
  * Example audio files are in `sample_data`; the audio has to be in .wav formatand mono-channel. For an example of how to do this, see `convert_trim.sh`

## Feature Extraction
  * Make sure the configurations are correct in `/conf`. For example:
    * I changed `fbank.conf` to also extract total energy by setting `--use-energy=true`
    * I used `mfcc_hires.conf` instead of the default `mfcc.conf`; according to the ASpiRE-related models, this gave better results in speech recognition
  * `comp_mfcc.sh`, `comp_fbank_energy.sh`, and `comp_pitch.sh` are sample scripts to extract mfcc, fbank, and pitch features. Note that the split channel part is repeated, comment this out if you've already done this. 


## Decoding Using a Pretrained Model
For my purposes (conversational speech, Switchboard), I'm using the [chain model](http://kaldi-asr.org/doc/chain.html) trained on Fisher data. The paper that this model is based on is [this one](http://www.danielpovey.com/files/2016_interspeech_mmi.pdf), and [this blog post](https://desh2608.github.io/2019-05-21-chain/) has some nice and detailed derivations. 

Steps:

  * Download a model from [kaldi models](http://kaldi-asr.org/models.html). For this example, I'm using the [ASpIRE chain model](http://kaldi-asr.org/models/m1), version with the precompiled HCLG
  * Untar it: `tar xvf 0001_aspire_chain_model_with_hclg.tar.bz2`
  * To this recipe, copy `cmd.sh` and `path.sh` if you haven't done so
  * Link common modules we'll be using (or copy all these here if you'll be editing the scripts in these directory):
    ```
    export KALDI_ROOT=/homes/ttmt001/kaldi
    ln -s $KALDI_ROOT/egs/aspire/s5/steps .
    ln -s $KALDI_ROOT/egs/aspire/s5/utils .
    ln -s $KALDI_ROOT/egs/aspire/s5/conf .
    ln -s $KALDI_ROOT/egs/aspire/s5/local .
    ```
  * Most instructions and comments are in `decode_audio.sh`
    * Steps 1 and 2 can be done first and then reused (model preparation, graph compilation)
    * Steps 3 and 4 can be run after creating `wav.scp` and `utt2spk` files in `my_data` folder. An example of creating those is in `my_data`

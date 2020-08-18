#!/user/bin/env python2


# BASED ON:
# /homes/ttmt001/transitory/seq2seq_parser/speech_parsing/enc_dec_parser/get_features.py

import os, sys, argparse
import cPickle as pickle
import glob, re
import json
import pandas as pd
import numpy as np
from numpy.polynomial import legendre

swbd_dir = "/g/ssli/data/CTS-English/swbd_align/swbd_features"
asr_dir = "/homes/ttmt001/transitory/asr_preps/asr_output/nbest"
feat_dir = "/s0/ttmt001/acoustic_features_json"
out_dir = "/s0/ttmt001"
fbank_stats_dict = pickle.load(open('/g/ssli/data/CTS-English/swbd_align/seq2seq_features/fbank_stats.pickle'))

with open('avg_word_stats.json', 'r') as f:
    dur_stats = json.load(f)
esize = 300
deg = 3

def pause2cat(p):
    if np.isnan(p):
        cat = 2
    elif p == 0.0:
        cat = 1
    elif p <= 0.05:
        cat = 3
    elif p <= 0.2:
        cat = 4
    elif p <= 1.0:
        cat = 5
    else:
        cat = 6
    return cat

def convert_to_array(str_vector):
    str_vec = str_vector.replace('[','').replace(']','').replace(',','').split()
    num_list = [float(x) for x in str_vec]
    return num_list

# NOTE: not used
def get_pitch_stats(pitch3, windices, file_name):
    pitch_stats = []
    for sidx, eidx in windices:
        if sidx < 0: sidx = 0
        this_frames = pitch3[:, sidx:eidx]
        if this_frames.size == 0:
            print "No frame in ", file_name, sidx, eidx
            this_stats = np.zeros(12,)
        else:
            max_pitch = np.max(this_frames, 1)
            min_pitch = np.min(this_frames, 1)
            mean_pitch = np.mean(this_frames, 1)
            slope = (this_frames[:,-1] - this_frames[:,0])/this_frames.shape[1]
            this_stats = np.hstack([max_pitch, min_pitch, mean_pitch, slope])
        pitch_stats.append(this_stats)
    return pitch_stats

# NOTE: not used
def get_pitch_coefs_feats(pitch3, windices, file_name):
    pitch_stats = []
    y = pitch3[:]
    # time is on 10ms steps
    t = np.linspace(0, y.shape[1]-1, y.shape[1]) * 0.01
    for sidx, eidx in windices:
        if sidx < 0: sidx = 0
        this_frames = pitch3[:, sidx:eidx]
        this_t = t[sidx:eidx]
        if this_frames.size == 0:
            print "No frame in ", file_name, sidx, eidx
            this_stats = np.zeros(12,)
        else:
            #max_pitch = np.max(this_frames, 1)
            #min_pitch = np.min(this_frames, 1)
            #mean_pitch = np.mean(this_frames, 1)
            #slope = (this_frames[:,-1] - this_frames[:,0])/this_frames.shape[1]
            coefs = legendre.legfit(this_t, this_frames.T, deg)
            #this_stats = np.hstack([max_pitch, min_pitch, mean_pitch, slope])
            #this_stats = coefs.reshape(12,)
        pitch_stats.append(coefs)
    stacked = np.vstack(pitch_stats)
    lo = np.min(stacked, 0)
    hi = np.max(stacked, 0)
    hilo = hi - lo
    pitch_stats = [(x - lo)/hilo for x in pitch_stats]
    pitch_stats = [x.reshape(12,) for x in pitch_stats]
    return pitch_stats

# NOTE: not used
def get_fbank_stats(fbank, partition, sf_name):
    lo_A = np.empty((3,0))
    hi_A = np.empty((3,0))
    for sidx, eidx in partition:
        if sidx < 0: sidx = 0
        this_frames = fbank[:, sidx:eidx]
        if this_frames.size == 0:
            print "No frame in ", sf_name, sidx, eidx
            continue
        e0 = [this_frames[0,:].min(), this_frames[0,:].max()]
        lo = np.sum(this_frames[1:21,:], axis=0)
        hi = np.sum(this_frames[21:,:], axis=0)
        elo = [min(lo), max(lo)]
        ehi = [min(hi), max(hi)]
        min_vec = np.array([e0[0], elo[0], ehi[0]]).reshape(3,1)
        max_vec = np.array([e0[1], elo[1], ehi[1]]).reshape(3,1)
        lo_A = np.hstack([lo_A, min_vec])
        hi_A = np.hstack([hi_A, max_vec])
    lo_A = np.min(lo_A, 1)
    hi_A = np.max(hi_A, 1)
    return lo_A, hi_A

# NOTE: not used
def normalize_mfccs(mfccs, windices, file_name):
    mfcc_stats = []
    for sidx, eidx in windices:
        if sidx < 0: sidx = 0
        this_frames = mfccs[:, sidx:eidx]
        if this_frames.size == 0:
            print "No frame in ", file_name, sidx, eidx
            this_stats = np.zeros(13,)
            continue
        mfcc_stats.append(this_frames)
    stacked = np.hstack(mfcc_stats)
    mu = np.mean(stacked, 1)
    si = np.std(stacked, 1)
    offset = mfccs - mu.reshape(13,1)
    mfcc_normed = offset/si.reshape(13,1)
    return mfcc_normed

# Based on ...seq2seq_parser/speech_parsing/enc_dec_parser/get_features.py
def get_time_features(start_times, end_times, sent_toks):
    sframes = [int(np.floor(x*100)) for x in start_times]
    eframes = [int(np.ceil(x*100)) for x in end_times]
    partition = zip(sframes, eframes)
    word_dur = [y-x for x,y in zip(start_times, end_times)]
    mean_wd = np.mean(word_dur) 
    sent_max = max(word_dur)
    dur_stats = [x/mean_wd for x in word_dur]
    word_dur = [x/sent_max for x in word_dur]
    pause_before = [6] # sentence boundary cat
    pause_after = []
    for i in range(1, len(start_times)):
        pause_before.append(pause2cat(start_times[i] - end_times[i-1]))
    for i in range(len(start_times)-1):
        pause_after.append(pause2cat(start_times[i+1] - end_times[i]))
    pause_after.append(6) 
    return partition, pause_before, pause_after, dur_stats, word_dur

def make_parser_feats_asr(split):
    info_file = os.path.join(asr_dir, split + '_asr_pa_nbest.tsv')
    info_df = pd.read_csv(info_file, sep="\t")
    info_df['prefix'] = info_df['orig_id'].apply(lambda x: x[:-5].replace('_','-'))
    info_df['start_times'] = info_df['start_times_asr'].apply(convert_to_array)
    info_df['end_times'] = info_df['end_times_asr'].apply(convert_to_array)

    dur_dict = {}
    pause_dict = {}
    pitch_dict = {}
    fbank_dict = {}
    partition_dict = {}
    #pcoef_dict = {}
    #mfcc_dict = {}

    for prefix, df_prefix in info_df.groupby('prefix'):
        print prefix
        pitch_file = os.path.join(feat_dir, 'pitch_json', prefix + '.json')
        with open(pitch_file, 'r') as fp:
            pitch_data = json.load(fp)
        fbank_file = os.path.join(feat_dir, 'fbank_json', prefix + '.json')
        with open(fbank_file, 'r') as ff:
            fbank_data = json.load(ff)
        for i, row in df_prefix.iterrows():
            sent_id = row.sent_id
            sent_toks = row.asr_sent
            start_times = row.start_times
            end_times = row.end_times
            partition_raw, pause_before, pause_after, dur_stats, word_dur = get_time_features(start_times, end_times, sent_toks)
            dur_dict[sent_id] = np.vstack([np.array(dur_stats), np.array(word_dur)])
            offset = partition_raw[0][0]
            partition = [(x-offset,y-offset) for x,y in partition_raw]
            partition_dict[sent_id] = partition
            pause_dict[sent_id] = {}
            pause_dict[sent_id]['pause_bef'] = pause_before
            pause_dict[sent_id]['pause_aft'] = pause_after
            
            #mfccs =  
            #mfcc_feats = normalize_mfccs(mfccs, partition, filename)

            pitch3 = pitch_data[partition_raw[0][0]:partition_raw[-1][-1]]
            pitch3 = np.array(pitch3).T
            fbank = fbank_data[partition_raw[0][0]:partition_raw[-1][-1]] 
            fbank = np.array(fbank).T
            minE, maxE = fbank_stats_dict[prefix.replace('-','_')]
            e0 = fbank[0,:]
            elo = np.sum(fbank[1:21,:], axis=0)
            ehi = np.sum(fbank[21:,:], axis=0)
            efeats = np.vstack([e0, elo, ehi])
            hilo = maxE.reshape(3,1) - minE.reshape(3,1)
            efeats = (efeats - minE.reshape(3,1))/hilo 

            #pitch_stats = get_pitch_feats(pitch3, partition, filename) 
            pitch_dict[sent_id] = pitch3
            fbank_dict[sent_id] = efeats
            #pcoef_dict[sent_id] = np.array(pitch_stats).T
            #mfcc_dict[sent_id] = mfccs

    dur_name = os.path.join(out_dir, split + '_asr_duration.pickle')
    pause_name = os.path.join(out_dir, split + '_asr_pause.pickle')
    partition_name = os.path.join(out_dir, split + '_asr_partition.pickle')
    pitch_name = os.path.join(out_dir, split + '_asr_pitch.pickle')
    fbank_name = os.path.join(out_dir, split + '_asr_fbank.pickle')
    #mfcc_name = os.path.join(out_dir, split + '_asr_mfcc.pickle')
    #pcoef_name = os.path.join(out_dir, split + '_asr_f0coefs.pickle')

    pickle.dump(dur_dict, open(dur_name, 'w'))
    pickle.dump(pause_dict, open(pause_name, 'w'))
    pickle.dump(partition_dict, open(partition_name, 'w'))
    pickle.dump(pitch_dict, open(pitch_name, 'w'))
    pickle.dump(fbank_dict, open(fbank_name, 'w'))
    #pickle.dump(mfcc_dict, open(mfcc_name, 'w'))
    #pickle.dump(pcoef_dict, open(pcoef_name, 'w'))


if __name__ == '__main__':
    pa = argparse.ArgumentParser(description = \
        "Preprocess segment files to get features")
    pa.add_argument('--split', type=str, \
        default="dev",\
        help="split")
    args = pa.parse_args()
    make_parser_feats_asr(args.split) 
    exit(0)
 

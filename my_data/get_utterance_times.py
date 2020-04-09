#!/usr/bin/env python3

import os
import argparse
import pandas as pd
import glob
import numpy as np
import json
# global dirs
sw_dir = '/g/ssli/data/CTS-English/swbd_align/'
sph_dir = '/g/ssli/data/swbdI/dist/swb1/'
wav_dir = '/s0/ttmt001/swbd_wav/'
dur_file = 'avg_word_stats.json'
threshold = 0.05 # ensuring kaldi can extract frames

with open(dur_file) as fin:
    avg_durs = json.load(fin)
global_mean = np.mean([x['mean'] for x in avg_durs.values() if x['count']>20])

def convert_to_array(str_vector):
    str_vec = str_vector.replace('[','').replace(']','').replace(',','').split()
    num_list = []
    for x in str_vec:
        x = x.strip()
        if x != 'None': num_list.append(float(x))
        else: num_list.append(np.nan)
    return num_list

def cleanup_times(tokens, start_times, end_times):
    tokens = tokens.strip().split()
    stimes = convert_to_array(start_times)
    etimes = convert_to_array(end_times)
    # left-right pass, to fix start times
    for j in range(1, len(tokens)):
        tok, stime = tokens[j], stimes[j]
        if stime < 0 or np.isnan(stime):
            stime = stimes[j-1]
            stimes[j] = stime
    # right-left pass, to fix end times
    if etimes[-1] < 0 or np.isnan(etimes[-1]):
        etimes[-1] = etimes[-2] if len(etimes) > 1 else -1
    for j in range(len(tokens)-1)[::-1]:
        tok, etime = tokens[j], etimes[j]
        if etime < 0 or np.isnan(etime): 
            etime = etimes[j+1]
            etimes[j] = etime  
    # etimes seem to be ok, only start times have issues
    for i in range(len(tokens)):
        tok = tokens[i]
        stime = stimes[i]
        etime = etimes[i]
        approx_dur = avg_durs[tok]['mean'] if tok in avg_durs else global_mean
        if (np.isnan(stime) or stime < 0) and etime > 0:
            stimes[i] = max(0, etime - approx_dur)
        if np.isnan(etime) or etime < 0:
            etimes[i] = stime + approx_dur
    utt_start = min(stimes) 
    utt_end = max(etimes)
    if utt_start >= utt_end:
        utt_end = utt_start + approx_dur
    if utt_end - utt_start < threshold:
        utt_end = utt_start + threshold
    return utt_start, utt_end
    
# NaN cases are usually for contractions
# -1 are usually for missed/inserted words
# if end time is NaN: use end time of next word
# if start time is NaN: use start time of prev word
def get_duration_stats(train_file):
    df = pd.read_csv(train_file, sep="\t")
    dur_dict = {}
    for i, row in df.iterrows():
        tokens = row.sentence.strip().split()
        stimes = convert_to_array(row.start_times)
        etimes = convert_to_array(row.end_times)
        # left-right pass, to fix start times
        for j in range(1, len(tokens)-1):
            tok, stime = tokens[j], stimes[j]
            if stime < 0:
                continue
            if np.isnan(stime):
                stime = stimes[j-1]
                stimes[j] = stime
        # right-left pass, to fix end times
        for j in range(1, len(tokens)-1)[::-1]:
            tok, etime = tokens[j], etimes[j]
            if etime < 0:
                continue
            if np.isnan(etime): 
                etime = etimes[j+1]
                etimes[j] = etime 
        tok, stime, etime = tokens[0], stimes[0], etimes[0]
        if np.isnan(stime) or stime < 0 or etime < 0:
            continue
        if np.isnan(etime): 
            etime = etimes[1]
            etimes[0] = etime
        word_dur = etime - stime
        if np.isnan(word_dur): print(i, j, stime, etime, tok)
        if tok not in dur_dict:
            dur_dict[tok] = []
        dur_dict[tok].append(word_dur)
        for j in range(1, len(tokens)-1):
            tok, stime, etime = tokens[j], stimes[j], etimes[j]
            if stime < 0 or etime < 0:
                continue
            word_dur = etime - stime
            if np.isnan(word_dur): print(i, j, etime, stime, tok)
            if tok not in dur_dict:
                dur_dict[tok] = []
            dur_dict[tok].append(word_dur)
        tok, stime, etime = tokens[-1], stimes[-1], etimes[-1]
        if np.isnan(etime) or etime < 0 or stime < 0:
            continue
        if np.isnan(stime):
            stime = stimes[-2]
            stimes[-1] = stime
        word_dur = etime - stime
        if np.isnan(word_dur): print(i, j, stime, etime, tok)
        if tok not in dur_dict:
            dur_dict[tok] = []
        dur_dict[tok].append(word_dur)
    return dur_dict

def write_dur_stats():
    train_file = '/g/ssli/data/CTS-English/swbd_align/swbd_trees/train2_mrg.tsv'
    stats = {}
    dur_stats = get_duration_stats(train_file)
    for word, times in dur_stats.items():
        stats[word] = {}
        stats[word]['count'] = len(times)
        stats[word]['mean'] = np.mean(times)
        stats[word]['std'] = np.std(times)
    outfile = 'avg_word_stats.json'
    with open(outfile, 'w') as fout:
        json.dump(stats, fout, indent=2)
    return

def get_start_time(times):
    time_list = times.replace('[','').replace(']','')
    time_list = time_list.split(',')
    time_list = [float(x) for x in time_list if 'None' not in x]
    time_list = [x for x in time_list if x >= 0]
    if len(time_list) > 0:
        return time_list[0]
    return None

def get_end_time(times):
    time_list = times.replace('[','').replace(']','')
    time_list = time_list.split(',')
    time_list = [float(x) for x in time_list if 'None' not in x]
    time_list = [x for x in time_list if x >= 0]
    if len(time_list) > 0:
        return time_list[-1]
    return None

def write_cmd_trim(task, split, cmd):
    out_dir = '/s0/ttmt001/utterances/' + task + '/' + split + '/'
    err = open(split + '_err_sents.txt', 'w')
    checks = []

    if not os.path.exists(out_dir):
        os.makedirs(out_dir, exist_ok=True)
    if task == 'parse':
        align_file = sw_dir + 'swbd_trees/{}_mrg.tsv'.format(split)
        align_df = pd.read_csv(align_file, sep="\t")
        files = set(align_df.file_id)
        align_df['start_time'] = align_df.apply(lambda row: cleanup_times(row.sentence, row.start_times, row.end_times)[0], axis=1)
        align_df['end_time'] = align_df.apply(lambda row: cleanup_times(row.sentence, row.start_times, row.end_times)[-1], axis=1)
        assert not align_df.isnull().values.any()
        file_column = 'file_id'
        sp_column = 'speaker'
    elif task == 'da':
        align_file = sw_dir + 'swda/data/swda_tsv/{}_aligned_merged.tsv'.format(split)
        align_df = pd.read_csv(align_file, sep="\t")
        files = set(align_df.filenum)
        file_column = 'filenum'
        sp_column = 'true_speaker'
    else:
        print("Need to specify task")
        exit(0)

    fout = open(cmd, 'w')
    fout.write("#!/bin/bash\n")

    for filenum in files:
        if task == 'da':
            oname = 'sw0' + str(filenum)
        else:
            oname = filenum.replace('sw', 'sw0')
        for speaker in ['A', 'B']:
            wav_in = wav_dir + oname + '_' + speaker + '.wav'
            side_df = align_df[(align_df[file_column]==filenum) & (align_df[sp_column]==speaker)]
            for i, row in side_df.iterrows():
                start_time = row.start_time
                end_time = row.end_time
                if task == 'da':
                    sent_id = '{}_{}_{}'.format(row.filenum, speaker, str(row.turn_id).zfill(4))
                else:
                    sent_id = row.sent_id.replace('~', '_{}_'.format(speaker))
                if start_time < 0 or end_time < 0 or start_time >= end_time:
                    err.write(sent_id + "\n")
                    print(i, sent_id, start_time, end_time)
                    continue
                utt_dur = end_time - start_time
                if utt_dur < threshold:
                    end_time = start_time + threshold
                    utt_dur = end_time - start_time
                checks.append(utt_dur)
                wav_out = out_dir + sent_id + '.wav'
                #fout.write('''echo "{}"\n'''.format(wav_out))
                item = "sox {} {} trim {} ={}\n".format(wav_in, wav_out, start_time, end_time)
                fout.write(item)

    fout.close()
    err.close()
    print("Stats on utterance durations:")
    print(min(checks), max(checks), np.mean(checks))
    return

def write_cmd_split(task, split, cmd):
    if task == 'parse':
        align_file = sw_dir + 'swbd_trees/{}_mrg.tsv'.format(split)
        align_df = pd.read_csv(align_file, sep="\t")
        files = set(align_df.file_id)
        files = [x.replace('sw','sw0')+'.sph' for x in files]
    elif task == 'da':
        align_file = sw_dir + 'swda/data/swda_tsv/{}_aligned_merged.tsv'.format(split)
        align_df = pd.read_csv(align_file, sep="\t")
        files = set(align_df.filenum)
        files = ['sw0'+str(x)+'.sph' for x in files]
    else:
        print("Need to specify task")
        exit(0)

    with open(cmd, 'w') as fout:
        fout.write("#!/bin/bash\n")
        fout.write("KALDI_HOME=/homes/ttmt001/kaldi/tools/sph2pipe_v2.5\n")
        for f in files:
            fname = sph_dir + f
            aname = wav_dir + f.replace('.sph', '_A.wav')
            item = "$KALDI_HOME/sph2pipe -f wav -p -c 1 {} {}\n".format(fname,aname)
            fout.write(item)
            bname = wav_dir + f.replace('.sph', '_B.wav')
            item = "$KALDI_HOME/sph2pipe -f wav -p -c 2 {} {}\n".format(fname,bname)
            fout.write(item)
    return

def main():
    """main function"""
    pa = argparse.ArgumentParser(
            description='Make script for extracting utterances from audiofiles')
    pa.add_argument('--split', help='data split', default='dev')
    pa.add_argument('--task', help='parse or da')
    pa.add_argument('--step', help='split or trim')
    args = pa.parse_args()
    # debug
    split = args.split
    task = args.task
    step = args.step
    cmd = 'cmd_{}_{}_{}.sh'.format(step, task, split)
    if step == 'split':
        write_cmd_split(task, split, cmd)
    elif step == 'trim':
        write_cmd_trim(task, split, cmd)
    else:
        print("Need to specify step")
    exit(0)


if __name__ == '__main__':
    main()


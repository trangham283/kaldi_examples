#!/usr/bin/env python3

import os
import argparse
import pandas as pd
import glob
import numpy as np
import json

# global dirs
sw_dir = '/g/ssli/data/CTS-English/swbd_align/'
out_dir = '/homes/ttmt001/transitory/asr_preps/asr_output/nbest/'

def make_df(asr_dir, task, split):
    ctm_file = os.path.join(asr_dir, "{}_{}".format(task, split), 
            "{}_{}_mapped.ctm".format(task, split))
    lm_file = os.path.join(asr_dir, "{}_{}".format(task, split), 
            "{}_{}.lmcost".format(task, split))
    ac_file = os.path.join(asr_dir, "{}_{}".format(task, split), 
            "{}_{}.accost".format(task, split))
    lines = open(ctm_file).readlines()
    lines = [x.strip().split() for x in lines]
    lms = open(lm_file).readlines()
    lms = [x.strip().split() for x in lms]
    lms = dict(lms)
    acs = open(ac_file).readlines()
    acs = [x.strip().split() for x in acs]
    acs = dict(acs)
    assert len(lms) == len(acs)
    list_row = []
    for sent_id, channel, start_time, duration, word in lines:
        list_row.append({'sent_id': sent_id,
            'start_time': float(start_time),
            'end_time': float(start_time) + float(duration),
            'word': word, 
            })
    df = pd.DataFrame(list_row)
    return df, acs, lms

SKIP = set(['[noise]', '[laughter]', '<unk>'])
SPLIT1 = {'gonna': 'gon na',
        'wanna': 'wan na',
        'gotta': 'got ta',
        "cannot": "can not",
        "dunno": "du n no",
        }
NO_SPLIT = set(["o'clock", "'cause", "'em", "'n", "'til"])
def split_toks(word):
    if "'" not in word:
        if word in SPLIT1:
            return SPLIT1[word]
        else:
            return word
    if word in NO_SPLIT:
        return word
    if word.startswith("'"):
        return word.replace("'", "` ")
    if word.endswith("'"):
        return word.replace("'", " '")
    if "n't" in word:
        return word.replace("n't", " n't")
    if "'" in word:
        if word == "y'all":
            return "y' all"
        else:
            temp = word.split("'")
            return temp[0] + " '" + temp[1]

def copy_times(row, name):
    len_toks = len(row.token.split())
    col = name + '_time'
    if len_toks == 1:
        times = [row[col]]
    else:
        times = [row[col]]*len_toks
    return times

def flatten_list(l):
    return [item for sublist in l for item in sublist]

def make_utt_df(df_raw, acs, lms):
    df_raw = df_raw[~df_raw.word.isin(SKIP)]
    df_raw['token'] = df_raw.word.apply(split_toks)
    df_raw['start_times_asr'] = df_raw.apply(lambda x: copy_times(x, 'start'), axis=1)
    df_raw['end_times_asr'] = df_raw.apply(lambda x: copy_times(x, 'end'), axis=1)
    df = df_raw.reset_index(drop=True)
    list_row = []
    for sent_id, sent_df in df.groupby('sent_id'):
        list_row.append({
            'sent_id': sent_id,
            'orig_id': sent_id.split('-')[0],
            'start_times_asr': flatten_list(sent_df.start_times_asr.to_list()),
            'end_times_asr': flatten_list(sent_df.end_times_asr.to_list()),
            'speaker': sent_id.split('-')[0][7],
            'asr_sent': ' '.join(sent_df.token.values),
            'lm_cost': float(lms[sent_id]),
            'ac_cost': float(acs[sent_id])
            })
    asr_df = pd.DataFrame(list_row)
    return asr_df

def process_pa(asr_dir, split):
    raw_df, acs, lms = make_df(asr_dir, 'pa', split)
    asr_df = make_utt_df(raw_df, acs, lms)
    asr_df = asr_df.rename(columns={'speaker': 'true_speaker'})
    pa_file = sw_dir + 'swbd_trees/parse_{}_times.tsv'.format(split)
    pa_df = pd.read_csv(pa_file, sep="\t")
    pa_df['sent_id'] = pa_df.apply(lambda row: row.sent_id.replace('~', "_{}_".format(row.speaker)), axis=1)
    #merged_df = pd.merge(asr_df, pa_df, on='sent_id', how='inner')
    #outname = out_dir + 'swbd_trees/{}_asr_mrg.tsv'.format(split)
    offsets = dict(zip(pa_df.sent_id, pa_df.start_time))
    mrgs = dict(zip(pa_df.sent_id, pa_df.mrg))
    pa_sents = dict(zip(pa_df.sent_id, pa_df.sentence))
    asr_df['mrg'] = asr_df['orig_id'].apply(lambda x: mrgs[x])
    asr_df['orig_sent'] = asr_df['orig_id'].apply(lambda x: pa_sents[x])
    # add offset since ASR times start at 0 for each utterance
    asr_df['start_times_asr'] = asr_df.apply(
        lambda row: [x + offsets[row.orig_id] for x in row.start_times_asr], 
        axis=1)
    asr_df['end_times_asr'] = asr_df.apply(
        lambda row: [x + offsets[row.orig_id] for x in row.end_times_asr], 
        axis=1)
    outname = out_dir + '{}_asr_pa_nbest.tsv'.format(split)
    asr_df.to_csv(outname, sep="\t", index=False)
    return

# FIXME
def process_da(asr_dir, split):
    raw_df = make_df(asr_dir, 'da', split)
    asr_df = make_utt_df(raw_df)
    da_file = sw_dir + 'swda/data/swda_tsv/{}_aligned_merged.tsv'.format(split)
    da_df = pd.read_csv(da_file, sep="\t")
    da_df['sent_id'] = da_df.apply(lambda row: "{}_{}_{}".format(row.filenum, row.true_speaker, str(row.turn_id).zfill(4)), axis=1)
    merged_df = pd.merge(asr_df, da_df, on='sent_id', how='inner')
    #outname = out_dir + 'swda/data/swda_tsv/{}_aligned_asr.tsv'.format(split)
    outname = out_dir + '{}_aligned_asr_nbest.tsv'.format(split)
    merged_df.to_csv(outname, sep="\t", index=False)
    return

def main():
    """main function"""
    pa = argparse.ArgumentParser(
            description='Prepare asr df')
    pa.add_argument('--asr_dir', help='asr output dir', 
            default='asr_output/nbest')
    pa.add_argument('--split', help='data split', default='dev')
    pa.add_argument('--task', help='pa or da')
    args = pa.parse_args()
    
    asr_dir = args.asr_dir
    split = args.split
    task = args.task

    if task == 'da':
        process_da(asr_dir, split)
    elif task == 'pa':
        process_pa(asr_dir, split)
    else:
        print("invalid task")
    
    exit(0)


if __name__ == '__main__':
    main()


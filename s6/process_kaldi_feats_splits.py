#!/user/bin/env python

import os
import sys
import pandas
import argparse
import numpy as np
import glob
import json

def process_feats(args):
    in_dir = args.in_dir
    out_dir = args.out_dir
    nsplit = int(args.nsplit)
    feattype = args.feattype
    raw_dir = os.path.join(in_dir, feattype)
    output_dir = os.path.join(out_dir, feattype, 'json')
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)
    if feattype == 'pitch':
        numc = 3
    elif feattype == 'mfcc':
        numc = 40
    elif feattype == 'fbank':
        numc = 41
    else:
        print("specify valid feattype: fbank, mfcc, or pitch")
        exit(0)

    for i in range(1, nsplit+1):
        raw_file = os.path.join(raw_dir,'raw_{}_swb1.{}.txt'.format(feattype,i))
        raw_lines = open(raw_file).readlines()
        sindices = [i for i,x in enumerate(raw_lines) if 'sw' in x]
        eindices = sindices[1:] + [len(raw_lines)]
        for start_idx, end_idx in zip(sindices, eindices):
            filename = raw_lines[start_idx].strip('[\n').rstrip().replace(\
                    'sw0', 'sw')
            frames = raw_lines[start_idx+1:end_idx]
            list_feats = [f.strip().split()[:numc] for f in frames]
            floated_feats = [[float(x) for x in coef] for coef in list_feats]
            full_name = os.path.join(output_dir, filename + '.json')
            with open(full_name, 'w') as fout:
                json.dump(floated_feats, fout, indent=2)

if __name__ == '__main__':
    pa = argparse.ArgumentParser(
            description='Process kaldi features')
    pa.add_argument('--nsplit', help='number of jobs when kaldi was called', \
            default=8)
    pa.add_argument('--in_dir', help='inpput directory', \
            default='/s0/ttmt001/kaldi-tutorial/kaldi_sample')
    pa.add_argument('--out_dir', help='output directory', \
            default='/s0/ttmt001/kaldi-tutorial/kaldi_sample')
    pa.add_argument('--feattype', help='feature type: fbank, mfcc, pitch', \
            default='pitch')
    args = pa.parse_args()
    process_feats(args)
    sys.exit(0)


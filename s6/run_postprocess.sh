#!/bin/bash
source /g/ssli/transitory/ttmt001/envs/py3.6-transformers-cpu/bin/activate
migrate --max-mem 16000 --max-cpu 3 --require TARGET.NikolaHost=="\"bird030\"" -f process_feats.cmd -J 3

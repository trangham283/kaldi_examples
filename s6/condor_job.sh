#!/bin/bash

migrate --max-mem 16000 --max-cpu 8 --require TARGET.NikolaHost=="\"bird030\"" "./comp_pitch.sh"
migrate --max-mem 16000 --max-cpu 8 --no-desktop "./comp_pitch.sh"

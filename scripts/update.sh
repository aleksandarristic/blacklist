#!/usr/bin/env bash

input_file="${1:-./update.txt}"
section="${2:-Scam}"
list="${3:-../lists/scam_hosts_srb.txt}"

./build_list.py -f ${input_file} -s ${section} -t ${list} --run
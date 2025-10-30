#!/usr/bin/env bash

section="${1:-Scam}"
list="${2:-../lists/scam_hosts_srb.txt}"

./build_list.py -f ./update.txt -s ${section} -t ${list} --run

#!/bin/bash
NUM_PROCESS=${1:-1}

cmd \
  open \
    -i "./scripts/sample.txt" \
    -i "./scripts/sample2.txt" \
    -f "txt" \
  txt2json \
  process \
    --num-process ${NUM_PROCESS} \
    --rule "shuffle" \
    -t 0.4 \
    -m 1.0 \
    -M 6.0 \
  save \
    -o "./results/eval.jsonl" \
    --stat

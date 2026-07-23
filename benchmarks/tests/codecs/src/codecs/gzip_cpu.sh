#!/bin/bash

DATASET=$1

if [ -z "$DATASET" ]; then
    echo "Usage: $0 <dataset>"
    exit 1
fi

OUTFILE=$(basename "$DATASET").gz
DECOMPFILE=$(basename "$DATASET").dec

GZIP=$(which gzip)

if [ -z "$GZIP" ]; then
    echo "STATUS=FAIL"
    exit 1
fi

INPUT_SIZE=$(stat -c%s "$DATASET")

START=$(date +%s%N)

gzip -c "$DATASET" > "$OUTFILE"

RET=$?

END=$(date +%s%N)

if [ $RET -ne 0 ]; then
    echo "STATUS=FAIL"
    exit $RET
fi

COMP_TIME_US=$(( (END - START) / 1000 ))

START=$(date +%s%N)

gzip -cd "$OUTFILE" > "$DECOMPFILE"

RET=$?

END=$(date +%s%N)

if [ $RET -ne 0 ]; then
    echo "STATUS=FAIL"
    exit $RET
fi

DECOMP_TIME_US=$(( (END - START) / 1000 ))

COMPRESSED_SIZE=$(stat -c%s "$OUTFILE")

RATIO=$(awk -v i="$INPUT_SIZE" -v c="$COMPRESSED_SIZE" \
'BEGIN { printf "%.6f", i/c }')

COMP_RATE=$(awk -v i="$INPUT_SIZE" -v t="$COMP_TIME_US" \
'BEGIN { printf "%.6f", (i/1048576)/(t/1000000.0) }')

DECOMP_RATE=$(awk -v i="$INPUT_SIZE" -v t="$DECOMP_TIME_US" \
'BEGIN { printf "%.6f", (i/1048576)/(t/1000000.0) }')

echo "composite:compression_rate <double> = <empty>" >&2
echo "composite:compression_rate_many <double> = $COMP_RATE" >&2
echo "composite:decompression_rate <double> = <empty>" >&2
echo "composite:decompression_rate_many <double> = $DECOMP_RATE" >&2

echo "size:compressed_size <uint64> = $COMPRESSED_SIZE" >&2
echo "size:compression_ratio <double> = $RATIO" >&2
echo "size:decompressed_size <uint64> = $INPUT_SIZE" >&2
echo "size:uncompressed_size <uint64> = $INPUT_SIZE" >&2

echo "time:compress_many <uint32> = $COMP_TIME_US" >&2
echo "time:decompress_many <uint32> = $DECOMP_TIME_US" >&2

echo "RET=0"
echo "STATUS=PASS"

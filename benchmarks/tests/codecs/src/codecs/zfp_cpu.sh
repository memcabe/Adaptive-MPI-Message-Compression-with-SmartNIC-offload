#!/bin/bash

DATASET=$1

PRESSIO=$HOME/spack/opt/spack/linux-rocky8-zen4/gcc-13.2.0/libpressio-tools-0.4.7-ukvm35yyhsf6ecii2tfqxdr7um3v2uuq/bin/pressio

if [-z "$DATASET" ]; then
	echo "Usage: $0 <dataset>"
	exit 1
fi

OUTFILE=$(basename "$DATASET").zfp
DECOMPFILE=$(basename "$DATASET").dec

$PRESSIO \
	-i "$DATASET" \
	-t float \
	-d 1800 \
	-d 3600 \
	-b compressor=lz4 \
	-m time \
	-m size \
	-m error_stat \
	-m pearson \
	-m ssim \
	-m max_error \
	-m input_stats \
	-M all \
	-W "$DECOMPFILE"

RET=$?

echo "RET=$RET"

if [ $RET -ne =]; then
	echo "STATUS=FAIL"
	exit $RET
fi

echo "STATUS=PASS"

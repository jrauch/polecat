#!/bin/sh

DATEDIR=$(date +%Y%m%d%H%M)
OUTDIR="results/$DATEDIR.html"

if [ ! -e polecat.env ]
then
	virtualenv polecat.env
	. polecat.env/bin/activate
	pip install -r requirements.txt
fi

if [ ! -e results ]
then
	mkdir results
fi

. polecat.env/bin/activate
python ./polecat.py $1 > $OUTDIR

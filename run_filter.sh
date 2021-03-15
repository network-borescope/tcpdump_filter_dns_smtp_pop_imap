#!/bin/bash

for filename in data/*.txt; do
	echo "Processing $filename"
	python3 filter_dns_smtp_pop_imap.py < "$filename"
	mv "$filename" data/loaded
done

#!/usr/bin/env bash

JSONLZ4_INPUT=$1
DEJSONLZ4=~/bin/dejsonlz4

if [ ! -f "$DEJSONLZ4" ]; then
    echo "dejsonlz4 not found: $DEJSONLZ4" 1>&2
    exit 1
fi

if [ ! -f "$JSONLZ4_INPUT" ]; then
    echo "Input file not found: $JSONLZ4_INPUT" 1>&2
    exit 1
fi

$DEJSONLZ4 "$JSONLZ4_INPUT" |
jq -r 'recurse(.children[]?) |
       pick(.dateAdded, .title) |
       (((.dateAdded/1000000) |
          strftime("%Y-%m-%d.%H%M: ")) + .title)' |
      sort |
      less

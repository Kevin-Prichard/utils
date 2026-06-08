#!/usr/bin/env bash

find ~ -type d -iname "firefox" -print0 |
    xargs -0I{} find "{}" -iname "bookmarkbackups" |
    sort -u |
    perl -ane 'chop; print "$_\x00"' |
    xargs -0I{} sh -c 'find "{}" | grep jsonlz4 | sort -r | head -1' |
    sort

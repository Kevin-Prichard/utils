#!/usr/bin/env bash

find *_files -type d -print0 |
    xargs -0I{} \
        find {} \
        -type f \
            \( \
            -size -1000k \
            -not -iname '*.jpg' \
            -not -iname '*.jpeg' \
            -not -iname '*.png' \
            \) \
            -or \
            \( \
            -size -5k \
            -iname '*.png' \
            \) -print0 |
    xargs -0I{} rm "{}"

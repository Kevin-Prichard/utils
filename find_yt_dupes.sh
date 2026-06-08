#!/usr/bin/env bash

find -L . -regextype posix-extended -iregex '.*\.(mp4|webm)' |
    perl -ane '

chop;
my ($i)=$_=~/\[([0-9a-z_\-]{11})\]/i;

push @{$z{$i}},$_ if $i and !-l $_;

END {
    $"="\t";
    foreach$i(sort keys %z) {
        if($#{$z{$i}} > 1) {
            for$fn(sort @{$z{$i}}) {
                my @t=(stat $fn);
                print "$t[7]\t$fn\n";
            }
        }
    }
}'

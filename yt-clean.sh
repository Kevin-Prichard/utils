#!/usr/bin/env bash


perl -ane '
    ($id) = $_ =~ m|ERROR: \[youtube\] ([a-zA-Z0-9_-]{11}):|;
    push @a, $id if $id;
    END{
        $"="\n";
        print"@a\n";
    }
' | sort -u

#!/usr/bin/env python3

from primePy.primes import between
import sys

lower = int(sys.argv[1]) if len(sys.argv) >= 2 else 11
upper = int(sys.argv[2]) if len(sys.argv) >= 3 else 99
len_limit = int(sys.argv[3]) if len(sys.argv) == 4 else 0

primes = between(lower, upper)

rev = lambda s: "".join([s[c] for c in range(len(s)-1, -1, -1)])

for x in primes:
    for y in primes:
        if x != y:
            prod = x * y
            if not len_limit or len(str(prod)) == len_limit:
                print(f"{x} * {y} = {x * y}")

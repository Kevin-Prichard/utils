#!/usr/bin/env python3.11

import argparse
from random import randint, random, seed
import sys
from typing import List


# Typical base 64 charset: most password filters accept
charset1 = [
    (45, 46),   # hy-phen
    (48, 58),   # 0-9
    (64, 91),   # A-Z
    (95, 96),   # under_score
    (97, 123),  # a-z
]

# all printable characters: some password filters don't accept (eg aliexpress)
charset2 = [
    (32, 127),  # space thru tilde
]

charset3 = [(0, 256)]


def get_args(argv):
    parser = argparse.ArgumentParser(
        prog="Random string/password generator",
        description="",
    )
    parser.add_argument(dest="word_len", type=int, action="store",
                        help="Number of random characters to produce")
    parser.add_argument(dest="charset", type=int,  action="store",
                        help='Which charset #, 1: base64, 2: typeable ASCII')
    parser.add_argument(dest="seed_times", type=int, action="store",
                        help='Number of times to reseed per char')
    parser.add_argument(dest="hex_encode", type=int, action="store",
                        help='Output as hex-encoded')
    return parser.parse_args(argv)


def gen_randstr(word_len: int, charset: list, seed_times, raw: bool=False):
    base_digits = [chr(c) for s in charset for c in range(s[0], s[1])]
    alph_len = len(base_digits)

    pw = []

    for i in range(seed_times):
        seed(randint(1, 2 ** 63 - 1))
    while len(pw) < word_len:
        if raw:
            pw.append(int(random() * alph_len))
        else:
            pw.append(base_digits[int(random() * alph_len)])

    if raw:
        return pw
    return "".join(pw)


def get_randstr(charset_num, word_len, hex_encode=0, seed_times=17):
    charset: List
    match args.charset:
        case 2:
            # Printable ASCII: 0x20-0x7E
            charset = charset2
        case 3:
            # Bytes: 0-255
            charset = charset3
        case _:
            # Base 64: alphanum + [_-]
            charset = charset1

    r = gen_randstr(args.word_len, charset, args.seed_times)
    if args.hex_encode:
        r = "".join(hex(ord(c))[2:] for c in r)
    return r


if __name__ == "__main__":
    args = get_args(sys.argv[1:])
    rand_str = get_randstr(
        args.charset, args.word_len, args.hex_encode, args.seed_times)
    print(rand_str)

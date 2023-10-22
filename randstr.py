#!/usr/bin/env python3.11

import argparse
from random import randint, random, seed
import sys
from typing import List


# Typical base 64 charset: most password filters accept
char_range_base64 = [
    (45, 46),   # hy-phen
    (48, 58),   # 0-9
    (65, 91),   # A-Z
    (95, 96),   # under_score
    (97, 123),  # a-z
]

# all printable characters: some password filters don't accept (eg aliexpress)
char_range_ascii = [
    (32, 127),  # space thru tilde
]

char_range_byte = [(0, 256)]


def make_charset(charset_ranges):
    return [chr(char) for subset in charset_ranges
            for char in range(subset[0], subset[1])]


CHARSET_BASE64 = make_charset(char_range_base64)
CHARSET_ASCII = make_charset(char_range_ascii)
CHARSET_BYTE = make_charset(char_range_byte)
CHARSETS={
    "BASE64": CHARSET_BASE64,
    "ASCII": CHARSET_ASCII,
    "BYTE": CHARSET_BYTE,
}


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


def make_randstr(word_len: int, base_digits: list, seed_times, raw: bool=False):
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


def gen_randstr(charset_num, word_len, hex_encode=0, seed_times=17):
    charset: List
    match charset_num:
        case 2:
            # Printable ASCII: 0x20-0x7E
            charset = CHARSET_ASCII
        case 3:
            # Bytes: 0-255
            charset = CHARSET_BYTE
        case _:
            # Base 64: alphanum + [_-]
            charset = CHARSET_BASE64

    r = make_randstr(word_len, charset, seed_times)
    if hex_encode:
        r = "".join(hex(ord(c))[2:] for c in r)
    return r


if __name__ == "__main__":
    args = get_args(sys.argv[1:])
    rand_str = gen_randstr(
        args.charset, args.word_len, args.hex_encode, args.seed_times)
    print(rand_str)

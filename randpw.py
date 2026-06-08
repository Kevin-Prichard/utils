#!/usr/bin/env python3

import struct
import sys
from typing import Generator


# Typical base 64 charset: most password filters accept
CHAR_RANGES_BASE64 = [
    (45, 46),   # hy-phen
    (48, 58),   # 0-9
    (65, 91),   # A-Z
    (95, 96),   # under_score
    (97, 123),  # a-z
]


def make_charset(charset_ranges):
    return [chr(char) for subset in charset_ranges
            for char in range(subset[0], subset[1])]


CHARSET_BASE64 = make_charset(CHAR_RANGES_BASE64)


def rand_i32(upper_bound: int) -> Generator[int, None, int]:
    # returns random integer in the range: 0 .. upper_bound - 1
    with open("/dev/random", "rb") as rand_raw:  # ash
        while True:
            rand_val = abs(struct.unpack("I", rand_raw.read(4))[0])
            yield int(rand_val / 2 ** 32 * upper_bound)


def randstr(length: int) -> str:
    charset_length = len(CHARSET_BASE64)
    random_string = []
    rand_char_gen = rand_i32(charset_length)
    while len(random_string) < length:
        random_string.append(CHARSET_BASE64[next(rand_char_gen)])
    return "".join(random_string)


def main():
    try:
        num_chars_to_generate = int(sys.argv[1])
        print(randstr(num_chars_to_generate))
    except (ValueError, IndexError):
        print("Specify the password length you want:\n$ ./randpw.py 25")


if __name__ == "__main__":
    main()

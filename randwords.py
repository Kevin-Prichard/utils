#!/usr/bin/env python3

from argparse import ArgumentParser, Namespace
import os
import re
import struct
import sys
from typing import Tuple, List, Generator

from randstr import CHARSETS


DICT_ROOT_PATH = "/usr/share/dict/"
DICTIONARIES = ["american-english", "british-english", "cracklib-small"]

# Used to skip words containing punctuation, like contractions, hyphenates
CLEAN_WORD_RX = re.compile(r"^[a-z0-9]+$", re.I)


def get_args(args: List[str]) -> Tuple[Namespace, List]:
    parser = ArgumentParser(
        prog='Generate random word phrase',
        description='Generate random word phrase from system dictionary')

    parser.add_argument(
        '--word-count', '-c', dest='word_count', type=int, action='store',
        default=4, help="Number of random words")
    parser.add_argument(
        '--min-len', '-n', dest='min_len', type=int, action='store',
        default=8, help="Minimum word length")
    parser.add_argument(
        '--max-len', '-x', dest='max_len', type=int, action='store',
        default=14, help="Maximum word length")
    parser.add_argument(
        '--sep', '-s', dest='sep', type=str, action='store',
        default="-", help="Separator between words")
    parser.add_argument(
        '--spoil', '-l', dest='spoiling', type=float, action='store',
        default=0.0, help="Spoil the spelling to increase randomisity"
    )
    parser.add_argument(
        '--spoil-charset', '-p', dest='spoil_charset', type=str, action='store',
        default='BASE64', help="Charset with which to do the spoiling"
    )

    return parser.parse_args(args), parser._actions


def rand_i32(upper_bound) -> Generator[int, None, int]:
    # returns random integer in the range: 0 .. upper_bound - 1
    with open("/dev/random", "rb") as rand_raw:  # ash
        while True:
            rand_val = abs(struct.unpack("I", rand_raw.read(4))[0])
            yield int(rand_val / 2 ** 32 * upper_bound)


def spoil(s, spoiling, charset):
    # Spoil string 's' by replacing chars at random locations with
    # chars randomly chosen from 'charset'
    wl = len(s)
    word = list(s)

    for i in range(round(spoiling * wl)):
        word[next(rand_i32(wl))] = charset[next(rand_i32(len(charset) - 1))]

    return "".join(word)


def gen_phrase(word_count, min_len, max_len, sep, spoiling, charset):
    # load all dictionaries  TODO let's parameterise dictionaries
    wordset = set()
    for dictionary in DICTIONARIES:
        with open(os.path.join(DICT_ROOT_PATH, dictionary), "r") as F:
            wordset.update(word.lower() for word in F.readlines())

    words = list(wordset)

    pw = []
    while len(pw) < word_count:
        # get random word
        word = words[next(rand_i32(len(words)))].strip()
        # add if word within length range desired and not a contraction?
        word_len = len(word)
        if (min_len <= word_len <= max_len
            and CLEAN_WORD_RX.match(word)
            and word not in pw):
            pw.append(spoil(word.strip(), spoiling, charset=charset))

    # return phrase
    return sep.join(pw)


def check_args_exist(args, actions, required_args):
    # Ensure all required args have values
    options = {action.dest: action.option_strings[0]
               for action in actions}

    errors = []
    for arg_name in required_args:
        if not args.__dict__[arg_name]:
            errors.append(options[arg_name])
    if errors:
        raise ValueError(f"Missing required parameters: {', '.join(errors)}")


def main(argv):
    args, actions = get_args(argv[1:])
    check_args_exist(args, actions, ["word_count", "min_len", "max_len"])
    spoil_charset = CHARSETS[args.spoil_charset]
    rand_phrase = gen_phrase(
        word_count=args.word_count,
        min_len=args.min_len,
        max_len=args.max_len,
        sep=args.sep,
        spoiling=args.spoiling,
        charset=spoil_charset)
    print(rand_phrase)


if __name__ == '__main__':
    main(sys.argv)

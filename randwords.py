#!/usr/bin/env python3

from argparse import ArgumentParser, Namespace
from random import randint
import sys
from typing import Tuple, List


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
        '--seed', '-r', dest='seed', type=int, action='store',
        default=17,
        help="Random seed to start, 0 uses first random int as seed")
    parser.add_argument(
        '--sep', '-s', dest='sep', type=str, action='store',
        default="-", help="Separator between words")

    return parser.parse_args(args), parser._actions


def gen_phrase(word_count, min_len, max_len, seed, sep):
    with open("/usr/share/dict/combined-english", "r") as F:
        words = F.readlines()

    pw = []
    for i in range(int(seed)):
        _ = randint(0, len(words))
    while len(pw) < word_count:
        word = words[randint(0, len(words))].strip()
        word_len = len(word)
        if (min_len <= word_len <= max_len and " " not in
                word and "-" not in word and "'" not in word):
            pw.append(word.strip())

    return sep.join(pw)


def check_args_exist(args, actions, required_args):
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
    rand_phrase = gen_phrase(
        args.word_count, args.min_len, args.max_len, args.seed, args.sep)
    print(rand_phrase)


if __name__ == '__main__':
    main(sys.argv)

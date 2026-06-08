#!/usr/bin/env python3

import difflib as diff
import sys


def load_log(pathname):
    with open(pathname, "r") as fh:
        return set(fh.readlines())


def load_log_set(pathname):
    with open(pathname, "r") as fh:
        return set(fh.readlines())


def main(logpath1, logpath2):
    # import pudb; pu.db
    l1 = load_log_set(logpath1)
    l2 = load_log_set(logpath2)

    new_l1 = l1 -l2
    new_l2 = l2 -l1
    print(f"new_l1: {len(new_l1)}")
    print(f"new_l2: {len(new_l2)}")
    return new_l1, new_l2

    # return diff.unified_diff(l1,l2)
    # import pudb; pu.db


if __name__ == "__main__":
    # import pudb; pu.db
    d1, d2 = main(*sys.argv[1:])
    # while a = next(d):
    import pudb; pu.db
    x = 1

#!/usr/bin/env python3

import sqlite3
import sys
from typing import List

from randwords import init_words

import wn


def init_wn(wn_base="oewn:2023"):
    loaded = 0
    lang = None
    while loaded < 1:
        try:
            lang = wn.Wordnet(wn_base)
            loaded += 1
        except sqlite3.OperationalError as load_exc:
            loaded -= 1
            if loaded < -1:
                raise RuntimeError(f"Could not load WordNet: {load_exc}")
            try:
                wn.download(wn_base)
                loaded += 1
            except Exception as download_exc:
                raise RuntimeError(
                    f"Could not download WordNet: {download_exc}")
    return lang


def get_interesting_words(concept_words: List[str]):
    init_words()
    # Find words that contain the concept words
    interesting_words = set()
    wnb = init_wn()
    for word in concept_words:
        ss = wnb.synsets(word)
        import pudb; pu.db
        for synset in wnb.synsets(word):
            for lemma in synset.lemmas():
                interesting_words.add(lemma.name())

    return interesting_words


def main(words):
    get_interesting_words(words)


if __name__ == "__main__":
    main(sys.argv[1:])

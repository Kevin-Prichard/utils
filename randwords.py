#!/usr/bin/env python3

from random import randint
import sys

wordcount, minwordlen, maxwordlen, scatter = (
    int(x) for x in sys.argv[1:5])
joinchar = sys.argv[5]
# e.g. ./randwords.py 4 5 8 10 -

with open("/usr/share/dict/combined-english", "r") as F:
    words = F.readlines()

pw = []
while len(pw) < wordcount:
    for i in range(int(scatter)):
        _ = randint(0, len(words))
    word = words[randint(0, len(words))].strip()
    word_len = len(word)
    if (minwordlen <= word_len <= maxwordlen and " " not in
            word and "-" not in word and "'" not in word):
        pw.append(word.strip())

print(joinchar.join(pw))

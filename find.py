import multiprocessing as mp
import re
from collections import ChainMap
from typing import Dict, TextIO

import click
import jellyfish


def find_matches(line: str, keyword: str, n: int) -> Dict[str, int]:
    '''Finds the best n matches in a given line'''
    words: str = re.sub(r'[^a-zA-Z]+', ' ', line)  # replace everything that does not look like a character with a space
    similarity: Dict[str, int] = {}
    for word in set(words.split()):
        similarity[word] = jellyfish.levenshtein_distance(
            jellyfish.soundex(keyword),
            jellyfish.soundex(word))
    results = sorted(similarity, key=similarity.get)
    best_results: Dict[str, int] = {}
    for result in results[:n]:
        best_results[result] = similarity[result]
    return best_results

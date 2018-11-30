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


def _process_helper(args) -> Dict[str, float]:
    '''Passes all of the given arguments to find_matches and returns the result'''
    return find_matches(*args)


@click.command()
@click.argument('file', type=click.File('r'))
@click.argument('keyword')
@click.option('--n', '--number', 'n', default=5, type=int, help='How many words do you need? default is 5')
def main(file: TextIO, keyword: str, n: int) -> None:
    '''The program finds N words sounding similarly to a given KEYWORD in a FILE.'''

    cpu_count: int = mp.cpu_count()
    pool = mp.Pool(cpu_count)
    best_results: Dict[str, int] = {}
    while True:
        lines = [file.readline() for _ in range(cpu_count)]  # read a line for each cpu core
        if not any(lines):
            break
        job_args = [(line, keyword, n) for line in lines]
        buffer_results = pool.map(_process_helper, job_args)
        results_dict = dict(ChainMap(*buffer_results, best_results))  # make a single dict from a list of dicts
        best_results = {}
        for i in sorted(results_dict, key=results_dict.get)[:n]:  # keep only the best n results
            best_results[i] = results_dict[i]
    print('\n'.join(sorted(best_results, key=best_results.get)))


if __name__ == "__main__":
    main()

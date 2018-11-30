import multiprocessing as mp
import re
from collections import ChainMap
from difflib import SequenceMatcher
from typing import Dict, TextIO

import click


def soundex(input: str) -> str:
    '''returns soundex code of input string'''
    letter_map = {'b': 1, 'f': 1, 'p': 1, 'v': 1,
                  'c': 2, 'g': 2, 'j': 2, 'k': 2, 'q': 2, 's': 2, 'x': 2, 'z': 2,
                  'd': 3, 't': 3, 'l': 4, 'm': 5, 'n': 5, 'r': 6}
    input = input.lower()
    exclude = 'eyuioahw'
    result = []
    result.append(input[0])
    previous = letter_map.get(input[0], None)
    count = 1
    previous_vowel = False
    for letter in input[1:]:
        if letter not in exclude:
            letter_code = letter_map[letter]
            if (letter_code != previous) or (letter_code == previous and previous_vowel):
                result.append(letter_code)
                previous = letter_code
                count += 1
                previous_vowel = False
            if count == 4:
                break
        elif letter not in 'hw':
            previous_vowel = letter
    output = "".join(map(str, result)).upper()
    output = output+'0'*(4-len(output)) # pad to 4 letters
    return output


def _find_distance(str1: str, str2: str) -> float:
    if str1 == str2:
        return 0
    matcher = SequenceMatcher(isjunk=None, a=str1.upper(), b=str2.upper())
    return 1 - matcher.ratio()


def find_matches(line: str, keyword: str, n: int) -> Dict[str, float]:
    '''Finds the best n matches in a given line'''
    words: str = re.sub(r'[^a-zA-Z]+', ' ', line)  # replace everything that does not look like a character with a space
    similarity: Dict[str, float] = {}
    for word in set(words.split()):
        similarity[word] = _find_distance(soundex(keyword), soundex(word))
    results = sorted(similarity, key=similarity.get)
    best_results: Dict[str, float] = {}
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
    best_results: Dict[str, float] = {}
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

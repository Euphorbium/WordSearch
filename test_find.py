from click.testing import CliRunner

from find import find_matches, main


def test_find_matches():
    line = 'Lithuania (UK and US: Listeni/ˌlɪθuːˈeɪniə/,[11][12][13] Lithuanian: Lietuva'
    keyword = 'lituania'
    n = 5
    find_matches_result = find_matches(line, keyword, n)
    assert len(find_matches_result) == 5
    assert find_matches_result == {'Lietuva': 1, 'Listeni': 2, 'Lithuania': 0, 'Lithuanian': 1, 'l': 2}


def test_cli():
    runner = CliRunner()
    result = runner.invoke(main, ['wiki_lt.txt', 'lituania'])
    assert 'Lithuania' in result.output
    result = runner.invoke(main, ['wiki_lt.txt', 'lituania', '--n=10'])
    assert len(result.output.split()) == 10

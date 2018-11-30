from click.testing import CliRunner

from find import find_matches, main, soundex


def test_soundex():
    assert soundex('xxxx') == 'X000'
    assert soundex('lituania') == 'L350'
    assert soundex('robert') == soundex('rupert')
    assert soundex('Rubin') == 'R150'
    assert soundex('ashcraft') == soundex('ashcroft')
    assert soundex('Tymczak') == 'T522'
    assert soundex('Pfister') == 'P236'
    assert soundex('Honeyman') == 'H555'


def test_find_matches():
    line = 'Lithuania (UK and US: Listeni/ˌlɪθuːˈeɪniə/,[11][12][13] Lithuanian: Lietuva'
    keyword = 'lituania'
    n = 6
    find_matches_result = find_matches(line, keyword, n)
    assert len(find_matches_result) == 6
    assert find_matches_result == {'Lietuva': 0.25, 'Listeni': 0.25, 'Lithuania': 0, 'Lithuanian': 0.25, 'l': 0.5,
                                   'and': 0.5}


def test_cli():
    runner = CliRunner()
    result = runner.invoke(main, ['wiki_lt.txt', 'lituania'])
    assert 'Lithuania' in result.output
    result = runner.invoke(main, ['wiki_lt.txt', 'lituania', '--n=10'])
    assert len(result.output.split()) == 10

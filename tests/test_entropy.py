import pytest

from pwcheck.entropy import _humanize, _score, analyze, load_wordlist, pool_size


def test_empty_password():
    r = analyze("")
    assert r.score == 0 and r.entropy_bits == 0


def test_pool_size_classes():
    assert pool_size("abc") == 26
    assert pool_size("aBc1") == 26 + 26 + 10
    assert pool_size("aB1!") == 26 + 26 + 10 + 32


def test_common_password_is_weak():
    r = analyze("password")
    assert r.score == 0
    assert any("common" in w.lower() for w in r.warnings)


def test_sequence_detected():
    r = analyze("abcdef123456")
    assert any("sequence" in w.lower() for w in r.warnings)


def test_repeats_penalized():
    assert analyze("aaaaaaaaaaaa").entropy_bits < analyze("agkxpqzmtwrb").entropy_bits


def test_long_random_is_strong():
    r = analyze("t7#Kq!9vLm2$Xr8Zp4@w")
    assert r.score >= 3


def test_longer_beats_complex_but_short():
    assert analyze("correcthorsebatterystaple").entropy_bits > analyze("Tr0ub4d!").entropy_bits


def test_pool_size_non_ascii_and_space():
    assert pool_size("é") == 100
    assert pool_size("a b") == 26 + 1


def test_load_wordlist_normalises(tmp_path):
    f = tmp_path / "w.txt"
    f.write_text("Hunter2\n\n  Secret  \n")
    assert load_wordlist(str(f)) == {"hunter2", "secret"}


@pytest.mark.parametrize(
    ("seconds", "expected"),
    [
        (0.5, "instantly"),
        (1, "1 second"),
        (90, "1 minute"),
        (7200, "2 hours"),
        (60 * 60 * 24 * 365 * 1000 * 2, "2 millennia"),
        (1e30, "millions of years or more"),
    ],
)
def test_humanize(seconds, expected):
    assert _humanize(seconds) == expected


@pytest.mark.parametrize(
    ("bits", "score"), [(0, 0), (27.9, 0), (28, 1), (36, 2), (60, 3), (79.9, 3), (80, 4)]
)
def test_score_thresholds(bits, score):
    assert _score(bits) == score

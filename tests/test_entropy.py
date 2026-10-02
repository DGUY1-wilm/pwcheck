from pwcheck.entropy import analyze, pool_size


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

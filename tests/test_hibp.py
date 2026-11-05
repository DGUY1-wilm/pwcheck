import urllib.error
from unittest import mock

import pytest

from pwcheck.hibp import HIBPError, fetch_range, parse_range, pwned_count, split_hash


def test_known_sha1_split():
    # SHA-1("password") = 5BAA61E4C9B93F3F0682250B6CF8331B7EE68FD8
    prefix, suffix = split_hash("password")
    assert prefix == "5BAA6"
    assert suffix == "1E4C9B93F3F0682250B6CF8331B7EE68FD8"


def test_parse_range_match_and_miss():
    body = "AAAA:3\r\n1E4C9B93F3F0682250B6CF8331B7EE68FD8:9545824\r\nBBBB:0"
    assert parse_range(body, "1E4C9B93F3F0682250B6CF8331B7EE68FD8") == 9545824
    assert parse_range(body, "NOTPRESENT") == 0


def test_padding_entries_do_not_match():
    assert (
        parse_range("1E4C9B93F3F0682250B6CF8331B7EE68FD8:0", "1E4C9B93F3F0682250B6CF8331B7EE68FD8")
        == 0
    )


def test_only_prefix_is_sent():
    seen = []

    def fake_fetch(prefix):
        seen.append(prefix)
        return "1E4C9B93F3F0682250B6CF8331B7EE68FD8:42"

    assert pwned_count("password", fetch=fake_fetch) == 42
    assert seen == ["5BAA6"]  # never the full hash


# --- fetch_range: the only function that touches the network, tested with a fake urlopen ---


def _fake_urlopen(body: str):
    resp = mock.MagicMock()
    resp.__enter__.return_value.read.return_value = body.encode()
    return mock.MagicMock(return_value=resp)


def test_fetch_range_sends_only_prefix_with_padding_header():
    fake = _fake_urlopen("ABC:1")
    with mock.patch("urllib.request.urlopen", fake):
        assert fetch_range("5BAA6") == "ABC:1"
    request = fake.call_args.args[0]
    assert request.full_url == "https://api.pwnedpasswords.com/range/5BAA6"
    assert request.get_header("Add-padding") == "true"


def test_fetch_range_network_error_becomes_hibperror():
    fake = mock.MagicMock(side_effect=urllib.error.URLError("no route"))
    with mock.patch("urllib.request.urlopen", fake), pytest.raises(HIBPError):
        fetch_range("5BAA6")


@pytest.mark.parametrize("bad", ["", "5BAA", "5BAA61", "5baa6", "../x", "5BAA6?x=1"])
def test_fetch_range_rejects_anything_but_5_hex_chars(bad):
    with pytest.raises(ValueError):
        fetch_range(bad)


def test_parse_range_bad_count_is_zero():
    assert parse_range("ABC:notanumber", "ABC") == 0

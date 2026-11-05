from pwcheck.hibp import parse_range, pwned_count, split_hash


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
    assert parse_range("1E4C9B93F3F0682250B6CF8331B7EE68FD8:0", "1E4C9B93F3F0682250B6CF8331B7EE68FD8") == 0


def test_only_prefix_is_sent():
    seen = []

    def fake_fetch(prefix):
        seen.append(prefix)
        return "1E4C9B93F3F0682250B6CF8331B7EE68FD8:42"

    assert pwned_count("password", fetch=fake_fetch) == 42
    assert seen == ["5BAA6"]  # never the full hash

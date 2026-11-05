"""CLI tests: every exit code path, without real network calls or a real terminal."""

import io
import runpy

import pytest

from pwcheck import cli
from pwcheck.hibp import HIBPError

STRONG = "t7#Kq!9vLm2$Xr8Zp4@w"


@pytest.fixture
def stdin(monkeypatch: pytest.MonkeyPatch):
    def _set(text: str) -> None:
        monkeypatch.setattr("sys.stdin", io.StringIO(text + "\n"))

    return _set


def _fake_pwned(count: int):
    return lambda password: count


def test_strong_password_offline_exits_0(stdin, capsys):
    stdin(STRONG)
    assert cli.main(["--stdin", "--no-network"]) == 0
    out = capsys.readouterr().out
    assert "Strength" in out and "Breach check" not in out


def test_weak_password_exits_1(stdin):
    stdin("password")
    assert cli.main(["--stdin", "--no-network"]) == 1


def test_pwned_password_exits_2(stdin, monkeypatch, capsys):
    stdin(STRONG)
    monkeypatch.setattr(cli, "pwned_count", _fake_pwned(1234))
    assert cli.main(["--stdin"]) == 2
    assert "PWNED, seen 1,234 times" in capsys.readouterr().out


def test_not_found_in_breaches(stdin, monkeypatch, capsys):
    stdin(STRONG)
    monkeypatch.setattr(cli, "pwned_count", _fake_pwned(0))
    assert cli.main(["--stdin"]) == 0
    assert "not found in known breaches" in capsys.readouterr().out


def test_breach_check_unavailable_does_not_crash(stdin, monkeypatch, capsys):
    def boom(password: str) -> int:
        raise HIBPError("offline")

    stdin(STRONG)
    monkeypatch.setattr(cli, "pwned_count", boom)
    assert cli.main(["--stdin"]) == 0  # strength result still stands
    assert "Breach check: unavailable (offline)" in capsys.readouterr().out


def test_interactive_prompt_uses_getpass(monkeypatch):
    # The password must be read with getpass (hidden input), never as an argument.
    monkeypatch.setattr(cli.getpass, "getpass", lambda prompt: STRONG)
    assert cli.main(["--no-network"]) == 0


def test_custom_wordlist_marks_password_common(stdin, tmp_path):
    wordlist = tmp_path / "words.txt"
    wordlist.write_text(STRONG + "\n")
    stdin(STRONG)
    assert cli.main(["--stdin", "--no-network", "--wordlist", str(wordlist)]) == 1


def test_python_dash_m_entry_point(stdin, monkeypatch):
    stdin("password")
    monkeypatch.setattr("sys.argv", ["pwcheck", "--stdin", "--no-network"])
    with pytest.raises(SystemExit) as exc:
        runpy.run_module("pwcheck", run_name="__main__")
    assert exc.value.code == 1

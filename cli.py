"""Command-line interface for pwcheck."""
from __future__ import annotations

import argparse
import getpass
import sys

from . import __version__
from .entropy import analyze, load_wordlist
from .hibp import HIBPError, pwned_count

BAR_WIDTH = 20


def _bar(score: int) -> str:
    filled = int((score + 1) / 5 * BAR_WIDTH)
    return "[" + "#" * filled + "-" * (BAR_WIDTH - filled) + "]"


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="pwcheck",
        description="Check password strength and breach exposure (k-anonymity).",
    )
    p.add_argument("--stdin", action="store_true", help="read password from stdin")
    p.add_argument("--no-network", action="store_true", help="skip the HIBP breach check")
    p.add_argument("--wordlist", metavar="FILE", help="extra common-password list")
    p.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    # Deliberately NOT a positional argument: passwords on the command line
    # end up in shell history and process listings.
    password = sys.stdin.readline().rstrip("\n") if args.stdin else getpass.getpass("Password: ")

    wordlist = load_wordlist(args.wordlist) if args.wordlist else None
    result = analyze(password, wordlist)

    print(f"\nStrength : {_bar(result.score)} {result.label}")
    print(f"Entropy  : {result.entropy_bits} bits (pool size {result.pool_size}, length {result.length})")
    print(f"Crack time (offline, fast hash): {result.crack_time}")
    for w in result.warnings:
        print(f"  ! {w}")

    exit_code = 1 if result.score <= 1 else 0

    if not args.no_network:
        try:
            count = pwned_count(password)
        except HIBPError as exc:
            print(f"\nBreach check: unavailable ({exc})")
        else:
            if count:
                print(f"\nBreach check: PWNED, seen {count:,} times in known breaches. Do not use it.")
                exit_code = 2
            else:
                print("\nBreach check: not found in known breaches.")

    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())

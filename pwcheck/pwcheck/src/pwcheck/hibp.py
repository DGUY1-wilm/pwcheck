"""HaveIBeenPwned "Pwned Passwords" range API client using k-anonymity.

How it works
------------
1. SHA-1 hash the password locally.
2. Send ONLY the first 5 hex characters (the prefix) to the API.
3. The API returns every known hash suffix sharing that prefix (hundreds).
4. We compare our remaining 35 characters locally.

The password, and its full hash, never leave the machine.
Docs: https://haveibeenpwned.com/API/v3#PwnedPasswords
"""
from __future__ import annotations

import hashlib
import urllib.error
import urllib.request
from typing import Callable

API_URL = "https://api.pwnedpasswords.com/range/"
USER_AGENT = "pwcheck-educational-tool"


class HIBPError(RuntimeError):
    """Raised when the breach lookup fails (network, rate limit, etc.)."""


def split_hash(password: str) -> tuple[str, str]:
    """Return (5-char prefix, 35-char suffix) of the uppercase SHA-1 hex digest."""
    # SHA-1 is required by the HIBP API; it is not used here for security.
    digest = hashlib.sha1(password.encode("utf-8")).hexdigest().upper()  # noqa: S324
    return digest[:5], digest[5:]


def fetch_range(prefix: str, timeout: float = 5.0) -> str:
    """Fetch the raw range response body for a 5-character hash prefix."""
    req = urllib.request.Request(
        API_URL + prefix,
        headers={
            "User-Agent": USER_AGENT,
            # Pads responses with fake entries so response size leaks nothing.
            "Add-Padding": "true",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:  # noqa: S310
            return resp.read().decode("utf-8")
    except (urllib.error.URLError, TimeoutError) as exc:
        raise HIBPError(f"Could not reach HIBP API: {exc}") from exc


def parse_range(body: str, suffix: str) -> int:
    """Find `suffix` in a range response. Returns breach count (0 if absent).

    Padding entries have a count of 0, so they never register as a match.
    """
    for line in body.splitlines():
        candidate, _, count = line.partition(":")
        if candidate.strip().upper() == suffix:
            try:
                return int(count.strip())
            except ValueError:
                return 0
    return 0


def pwned_count(
    password: str,
    fetch: Callable[[str], str] = fetch_range,
) -> int:
    """Return how many times `password` appears in known breaches.

    `fetch` is injectable so tests can run without network access.
    """
    prefix, suffix = split_hash(password)
    return parse_range(fetch(prefix), suffix)

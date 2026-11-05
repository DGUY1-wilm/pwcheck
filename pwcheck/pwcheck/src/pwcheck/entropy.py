"""Entropy-based password strength estimation.

Method
------
1. Estimate the character pool size from the character classes used.
2. Base entropy = len(password) * log2(pool_size).
3. Subtract penalties for patterns that make guessing easier
   (repeated characters, keyboard/alphabet sequences).
4. Passwords found in a common-password list are capped at a very low entropy.

This is an *estimate*. It assumes characters are chosen uniformly at random,
which humans rarely do, so the penalties and the breach check matter.
"""
from __future__ import annotations

import math
import re
import string
from dataclasses import dataclass, field

# A tiny sample list for the demo. For real use, load a larger list
# (e.g. the top 100k from SecLists) via `load_wordlist()`.
COMMON_PASSWORDS = {
    "password", "123456", "12345678", "123456789", "qwerty", "abc123",
    "password1", "111111", "iloveyou", "admin", "letmein", "welcome",
    "monkey", "dragon", "football", "baseball", "master", "sunshine",
    "princess", "qwerty123", "1q2w3e4r", "passw0rd", "p@ssw0rd", "trustno1",
}

SEQUENCES = [
    string.ascii_lowercase,
    "qwertyuiop", "asdfghjkl", "zxcvbnm",
    string.digits,
]

# Assumed attacker speed: offline attack on a fast hash with a GPU rig.
GUESSES_PER_SECOND = 1e10

LABELS = ["Very weak", "Weak", "Fair", "Strong", "Very strong"]


@dataclass
class StrengthResult:
    length: int
    pool_size: int
    entropy_bits: float
    score: int  # 0-4
    label: str
    crack_time: str
    warnings: list[str] = field(default_factory=list)


def load_wordlist(path: str) -> set[str]:
    """Load a newline-delimited wordlist into a lowercase set."""
    with open(path, encoding="utf-8", errors="ignore") as fh:
        return {line.strip().lower() for line in fh if line.strip()}


def pool_size(password: str) -> int:
    size = 0
    if re.search(r"[a-z]", password):
        size += 26
    if re.search(r"[A-Z]", password):
        size += 26
    if re.search(r"\d", password):
        size += 10
    if re.search(r"[%s]" % re.escape(string.punctuation), password):
        size += len(string.punctuation)  # 32
    if re.search(r"[^\x00-\x7f]", password):
        size += 100  # rough allowance for non-ASCII characters
    if re.search(r"\s", password):
        size += 1
    return size


def _repeat_penalty(password: str) -> float:
    """Bits to subtract for runs like 'aaaa' (each repeat adds ~no entropy)."""
    penalty = 0.0
    per_char = math.log2(max(pool_size(password), 2))
    for match in re.finditer(r"(.)\1+", password):
        extra_chars = len(match.group(0)) - 1
        penalty += extra_chars * per_char
    return penalty


def _sequence_penalty(password: str) -> tuple[float, bool]:
    """Detect runs of 3+ characters from alphabet/keyboard/digit sequences."""
    lowered = password.lower()
    penalty, found = 0.0, False
    per_char = math.log2(max(pool_size(password), 2))
    for seq in SEQUENCES:
        for forward in (seq, seq[::-1]):
            for i in range(len(forward) - 2):
                if forward[i : i + 3] in lowered:
                    found = True
                    penalty += per_char * 2
    return penalty, found


def _humanize(seconds: float) -> str:
    if seconds < 1:
        return "instantly"
    units = [
        ("second", 60), ("minute", 60), ("hour", 24), ("day", 365),
        ("year", 100), ("century", 10), ("millennium", 1000),
    ]
    value = seconds
    for name, step in units:
        if value < step:
            n = int(value)
            if n == 1:
                return f"1 {name}"
            plural = "millennia" if name == "millennium" else name + "s"
            return f"{n} {plural}"
        value /= step
    return "millions of years or more"


def _score(bits: float) -> int:
    if bits < 28:
        return 0
    if bits < 36:
        return 1
    if bits < 60:
        return 2
    if bits < 80:
        return 3
    return 4


def analyze(password: str, wordlist: set[str] | None = None) -> StrengthResult:
    """Return a StrengthResult for `password`."""
    warnings: list[str] = []
    words = COMMON_PASSWORDS if wordlist is None else (COMMON_PASSWORDS | wordlist)

    if not password:
        return StrengthResult(0, 0, 0.0, 0, LABELS[0], "instantly", ["Empty password."])

    size = pool_size(password)
    bits = len(password) * math.log2(max(size, 2))

    bits -= _repeat_penalty(password)
    if re.search(r"(.)\1{2,}", password):
        warnings.append("Contains repeated characters.")

    seq_penalty, has_seq = _sequence_penalty(password)
    bits -= seq_penalty
    if has_seq:
        warnings.append("Contains an alphabet, keyboard, or number sequence.")

    if password.lower() in words:
        bits = min(bits, 10.0)
        warnings.append("This is a very common password.")

    if len(password) < 12:
        warnings.append("Shorter than 12 characters; length matters most.")

    bits = max(bits, 0.0)
    seconds = (2 ** bits) / 2 / GUESSES_PER_SECOND  # average case: half the space
    score = _score(bits)

    return StrengthResult(
        length=len(password),
        pool_size=size,
        entropy_bits=round(bits, 1),
        score=score,
        label=LABELS[score],
        crack_time=_humanize(seconds),
        warnings=warnings,
    )

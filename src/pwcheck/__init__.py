"""pwcheck: password strength scoring + HaveIBeenPwned k-anonymity breach check."""

from .entropy import StrengthResult, analyze
from .hibp import pwned_count

__all__ = ["StrengthResult", "analyze", "pwned_count"]
__version__ = "0.1.0"

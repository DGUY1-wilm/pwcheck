# pwcheck

This is an in depth description of the pwcheck (password checker). See other README for easy step by step tutorial to perform on your own machine. 
A command-line password strength checker that scores passwords by **entropy** and checks whether they've appeared in known data breaches using the **HaveIBeenPwned k-anonymity API**, without ever sending your password (or its full hash) anywhere.

Standard library only. No dependencies.

## Install & run

```bash
git clone https://github.com/DGUY1-wilm/pwcheck.git
cd pwcheck
pip install -e .
pwcheck                 # prompts for a password (hidden input)
```

Other modes:

```bash
echo 'hunter2' | pwcheck --stdin         # read from stdin
pwcheck --no-network                     # entropy only, fully offline
pwcheck --wordlist rockyou-top100k.txt   # add a bigger common-password list
```

Exit codes: `0` ok, `1` weak, `2` found in a breach (handy for scripts / CI).

## Example output

```
Password: ********

Strength : [####----------------] Very weak
Entropy  : 10.0 bits (pool size 26, length 8)
Crack time (offline, fast hash): instantly
  ! This is a very common password.
  ! Shorter than 12 characters; length matters most.

Breach check: PWNED, seen 9,545,824 times in known breaches. Do not use it.
```

## How it works

### 1. Entropy scoring (`entropy.py`)
- Estimate the **character pool** (lowercase 26, uppercase 26, digits 10, symbols 32, ...).
- `entropy = length x log2(pool)`
- Subtract penalties for repeated characters and alphabet/keyboard/number sequences.
- Cap known-common passwords at ~10 bits.
- Map bits to a 0-4 score and an estimated offline crack time (assumes 10^10 guesses/sec, average case = half the keyspace).

### 2. Breach lookup with k-anonymity (`hibp.py`)

```
password --SHA-1--> 5BAA61E4C9B93F3F0682250B6CF8331B7EE68FD8
                    \___/ \_______________________________/
                   prefix              suffix
                  (sent to API)     (never leaves your machine)
```

1. Hash locally with SHA-1.
2. Send only the **first 5 hex characters** to `api.pwnedpasswords.com/range/{prefix}`.
3. The API returns every breached-hash suffix with that prefix (hundreds of candidates).
4. Compare your suffix **locally**.

The `Add-Padding` header is enabled so response size can't hint at which bucket you hit.

## Threat model

| Concern | Mitigation |
|---|---|
| Password leaked to the API | Only a 5-char hash prefix is sent; the API can't tell which of ~800 suffixes is yours |
| Password in shell history / `ps` | Not accepted as a CLI argument; read via `getpass` or stdin |
| Response-size side channel | `Add-Padding: true` |
| Network failure | Degrades gracefully; entropy score still shown |

**Limitations:**
- Entropy estimates assume random selection. Human-chosen passwords like `Summer2026!` score higher than they deserve. Production tools (e.g. zxcvbn) model dictionary words, leetspeak, dates, and names.
- SHA-1 is used only because the HIBP API requires it, not for any security purpose.
- The attacker-speed assumption is a rough model, not a guarantee.
- A malicious or compromised API endpoint could still observe your IP and the prefix.

## Tests

```bash
pip install -e ".[dev]"
pytest
```

Network calls are mocked via dependency injection (`pwned_count(pw, fetch=...)`), and a test asserts that only the 5-character prefix is ever passed to the fetcher.

## Roadmap ideas
- [ ] Dictionary-word and leetspeak detection (or integrate `zxcvbn`)
- [ ] Passphrase mode (Diceware word-count entropy)
- [ ] Batch mode for auditing a password-manager export (locally)
- [ ] Optional local HIBP hash file for fully offline checks
- [ ] Simple Flask/FastAPI web UI with client-side hashing

## License
MIT

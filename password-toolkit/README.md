# Password Toolkit


Generate secure passwords and passphrases, and check how strong an existing password is. Uses Python's `secrets` module (cryptographically secure), not `random`.

## Features
- Random passwords with a guaranteed mix of lowercase, uppercase, digits and symbols
- Word-based passphrases
- Strength checker with an entropy estimate and improvement tips
- No dependencies

## Usage
```bash
python passwords.py generate -l 20
python passwords.py generate -l 12 --no-symbols
python passwords.py passphrase -w 5
python passwords.py check "MyP@ssw0rd"
```

## Run the tests
```bash
pip install pytest
pytest
```

## What I practiced
Secure randomness with `secrets`, entropy basics, input validation, and test design for random output.

> The entropy figure is a rough estimate for learning purposes, not a security audit.

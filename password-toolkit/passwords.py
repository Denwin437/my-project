#!/usr/bin/env python3
"""Password Toolkit: secure password and passphrase generator plus a strength checker."""

import argparse
import math
import secrets
import string
import sys

COMMON_PASSWORDS = {
    "password", "123456", "12345678", "qwerty", "abc123", "letmein",
    "admin", "welcome", "iloveyou", "password1", "111111", "123456789",
}

WORDS = [
    "anchor", "bamboo", "candle", "dragon", "ember", "falcon", "garden", "harbor",
    "island", "jungle", "kettle", "lantern", "meadow", "nebula", "orchid", "pepper",
    "quartz", "river", "saddle", "thunder", "umbrella", "velvet", "willow", "yonder",
    "zephyr", "copper", "marble", "pixel", "rocket", "silver", "timber", "violet",
]

SYMBOLS = "!@#$%^&*()-_=+[]{};:,.?"


def generate_password(length: int = 16, upper: bool = True, digits: bool = True, symbols: bool = True) -> str:
    """Generate a random password containing at least one character of every enabled class."""
    pools = [string.ascii_lowercase]
    if upper:
        pools.append(string.ascii_uppercase)
    if digits:
        pools.append(string.digits)
    if symbols:
        pools.append(SYMBOLS)
    if length < len(pools):
        raise ValueError(f"Length must be at least {len(pools)} for the chosen options")
    chars = [secrets.choice(pool) for pool in pools]
    everything = "".join(pools)
    chars += [secrets.choice(everything) for _ in range(length - len(chars))]
    secrets.SystemRandom().shuffle(chars)
    return "".join(chars)


def generate_passphrase(words: int = 4, separator: str = "-") -> str:
    if words < 2:
        raise ValueError("A passphrase needs at least 2 words")
    return separator.join(secrets.choice(WORDS) for _ in range(words))


def entropy_bits(password: str) -> float:
    """Rough entropy estimate: length * log2(size of the character pool used)."""
    pool = 0
    if any(c in string.ascii_lowercase for c in password):
        pool += 26
    if any(c in string.ascii_uppercase for c in password):
        pool += 26
    if any(c in string.digits for c in password):
        pool += 10
    if any(not c.isalnum() for c in password):
        pool += len(SYMBOLS)
    return round(len(password) * math.log2(pool), 1) if pool else 0.0


def check_strength(password: str) -> dict:
    if not password:
        return {"label": "empty", "entropy": 0.0, "tips": ["Enter a password"]}
    tips = []
    if password.lower() in COMMON_PASSWORDS:
        return {
            "label": "very weak",
            "entropy": entropy_bits(password),
            "tips": ["This is a very common password"],
        }
    if len(password) < 12:
        tips.append("Use at least 12 characters")
    if password.lower() == password:
        tips.append("Add uppercase letters")
    if not any(c.isdigit() for c in password):
        tips.append("Add digits")
    if all(c.isalnum() for c in password):
        tips.append("Add symbols")
    bits = entropy_bits(password)
    label = "weak" if bits < 40 else "fair" if bits < 60 else "strong" if bits < 80 else "excellent"
    return {"label": label, "entropy": bits, "tips": tips}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Generate passwords and check their strength.")
    sub = parser.add_subparsers(dest="command", required=True)

    gen = sub.add_parser("generate", help="generate a random password")
    gen.add_argument("-l", "--length", type=int, default=16)
    gen.add_argument("--no-upper", action="store_true")
    gen.add_argument("--no-digits", action="store_true")
    gen.add_argument("--no-symbols", action="store_true")

    phrase = sub.add_parser("passphrase", help="generate a word-based passphrase")
    phrase.add_argument("-w", "--words", type=int, default=4)

    chk = sub.add_parser("check", help="rate a password's strength")
    chk.add_argument("password")

    args = parser.parse_args(argv)
    try:
        if args.command == "generate":
            print(generate_password(args.length, not args.no_upper, not args.no_digits, not args.no_symbols))
        elif args.command == "passphrase":
            print(generate_passphrase(args.words))
        else:
            result = check_strength(args.password)
            print(f"Strength: {result['label']} (~{result['entropy']} bits of entropy)")
            for tip in result["tips"]:
                print(f"  - {tip}")
    except ValueError as err:
        print(f"Error: {err}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

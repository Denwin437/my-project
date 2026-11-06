#!/usr/bin/env python3
"""Text Analyzer: word counts, top words, reading time and readability score."""

import argparse
import re
import sys
from collections import Counter
from pathlib import Path

STOP_WORDS = {
    "the", "a", "an", "and", "or", "but", "of", "to", "in", "on", "at", "is",
    "it", "that", "this", "for", "with", "as", "was", "are", "be", "by", "i",
}


def words(text: str) -> list:
    return re.findall(r"[a-zA-Z']+", text.lower())


def sentence_count(text: str) -> int:
    return len([s for s in re.split(r"[.!?]+", text) if s.strip()])


def word_frequency(text: str, top: int = 10, skip_stop_words: bool = True) -> list:
    tokens = [w for w in words(text) if not (skip_stop_words and w in STOP_WORDS)]
    return Counter(tokens).most_common(top)


def reading_time_minutes(text: str, wpm: int = 200) -> float:
    return round(len(words(text)) / wpm, 2)


def count_syllables(word: str) -> int:
    word = word.lower()
    count = len(re.findall(r"[aeiouy]+", word))
    if word.endswith("e") and not word.endswith("le") and count > 1:
        count -= 1
    return max(count, 1)


def flesch_reading_ease(text: str) -> float:
    tokens = words(text)
    sentences = sentence_count(text)
    if not tokens or not sentences:
        return 0.0
    syllables = sum(count_syllables(w) for w in tokens)
    score = 206.835 - 1.015 * (len(tokens) / sentences) - 84.6 * (syllables / len(tokens))
    return round(score, 1)


def analyze(text: str, top: int = 10) -> dict:
    return {
        "words": len(words(text)),
        "sentences": sentence_count(text),
        "reading_time_min": reading_time_minutes(text),
        "flesch_score": flesch_reading_ease(text),
        "top_words": word_frequency(text, top),
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Analyze a text file (or stdin).")
    parser.add_argument("file", nargs="?", type=Path, help="text file; reads stdin if omitted")
    parser.add_argument("--top", type=int, default=10, help="how many top words to show")
    args = parser.parse_args(argv)

    text = args.file.read_text(encoding="utf-8") if args.file else sys.stdin.read()
    result = analyze(text, args.top)
    print(f"Words:            {result['words']}")
    print(f"Sentences:        {result['sentences']}")
    print(f"Reading time:     {result['reading_time_min']} min")
    print(f"Flesch score:     {result['flesch_score']} (higher = easier to read)")
    print("Top words:")
    for word, n in result["top_words"]:
        print(f"  {word:<15} {n}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

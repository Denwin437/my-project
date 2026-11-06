# Text Analyzer


A command-line tool that analyzes any text file: word count, sentence count, estimated reading time, most frequent words, and a Flesch reading-ease score.

## Features
- Word and sentence statistics
- Top-N most frequent words (common stop words ignored)
- Reading time at 200 words per minute
- Flesch Reading Ease readability score
- Reads from a file or from stdin, no dependencies

## Usage
```bash
python analyzer.py essay.txt --top 5
cat essay.txt | python analyzer.py
```

## Run the tests
```bash
pip install pytest
pytest
```

## What I practiced
Regular expressions, text processing with `collections.Counter`, implementing a published formula, and handling edge cases such as empty input.

## Limitations
Syllables are estimated with a simple vowel-group heuristic, so the Flesch score is an approximation (a few words such as "create" are miscounted). It is accurate enough to compare texts, not to publish exact grades.

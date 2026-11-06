# My Projects

![CI](https://github.com/Denwin437/my-project/actions/workflows/ci.yml/badge.svg) ![License](https://img.shields.io/badge/license-MIT-green)

A collection of small, tested projects built in Python and HTML/CSS. Every Python project has unit tests that run automatically on each push.

| Project | What it does | Stack |
|---------|--------------|-------|
| [url-shortener](url-shortener) | REST API that shortens URLs and tracks clicks | Flask, SQLite |
| [markdown-converter](markdown-converter) | Markdown to HTML converter built from scratch, XSS-safe | Python |
| [log-analyzer](log-analyzer) | Summarizes web server access logs | Python |
| [password-toolkit](password-toolkit) | Secure password generator and strength checker | Python |
| [task-tracker-cli](task-tracker-cli) | Command-line to-do manager with priorities | Python |
| [expense-tracker](expense-tracker) | Logs spending to CSV, summarizes by category or month | Python |
| [text-analyzer](text-analyzer) | Word stats, reading time and readability score | Python |
| [portfolio-website](portfolio-website) | Responsive personal portfolio site | HTML, CSS |

## Running a project
Each folder has its own README with usage and test instructions. For example:

```bash
cd url-shortener
pip install -r requirements.txt
pytest
```

## License
MIT, see [LICENSE](LICENSE).

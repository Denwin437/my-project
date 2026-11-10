# Python Projects

<img src="https://github.com/Denwin437/my-project/actions/workflows/ci.yml/badge.svg" alt="CI" /> <img src="https://img.shields.io/badge/python-3.10%2B-3776AB?logo=python&logoColor=white" alt="Python 3.10+" /> <img src="https://img.shields.io/badge/license-MIT-blue" alt="MIT license" />

Eleven self-contained projects, each with its own README, unit tests and automated CI. They cover command-line tools, a REST API, text and log processing, and security-minded input handling.

## Projects

| Project | What it does | Stack | Tests |
|---------|--------------|-------|:-----:|
| [**url-shortener**](url-shortener) | REST API that shortens URLs, redirects and counts clicks | Flask · SQLite | 5 |
| [**markdown-converter**](markdown-converter) | Markdown → HTML converter written from scratch, safe against HTML injection | Python | 12 |
| [**log-analyzer**](log-analyzer) | Summarizes web server logs: status codes, error rate, top IPs and paths | Python | 6 |
| [**password-toolkit**](password-toolkit) | Secure password and passphrase generator with a strength checker | Python · `secrets` | 8 |
| [**task-tracker-cli**](task-tracker-cli) | Command-line to-do manager with priorities | Python | 6 |
| [**expense-tracker**](expense-tracker) | Logs spending to CSV and summarizes by category or month | Python | 5 |
| [**text-analyzer**](text-analyzer) | Word statistics, reading time and a readability score | Python | 7 |
| [**file-organizer**](file-organizer) | Sorts a folder by file type or month, with dry-run and undo; never overwrites | Python | 31 |
| [**student-management**](student-management) | REST API for student records with search, filters, pagination and stats | FastAPI · SQLite | 18 |
| [**qr-generator**](qr-generator) | QR codes for text, links, Wi-Fi and contacts as PNG or SVG | Python · qrcode | 17 |
| [**portfolio-website**](portfolio-website) | Responsive dark-theme personal site | HTML · CSS | n/a |

## Engineering practices

- **Tested:** 115 automated tests, including CLI end-to-end tests and API tests with Flask's test client.
- **Continuous integration:** GitHub Actions lints with ruff and runs every project's tests on Python 3.10 and 3.12 for each push and pull request.
- **Maintained:** Dependabot updates, issue and PR templates, a security policy and a changelog.
- **Secure by default:** cryptographically secure randomness (`secrets`), HTML escaping and URL-scheme filtering, and parameterized SQL queries.
- **Input validation:** every CLI and API rejects bad input with clear errors instead of crashing.
- **Minimal dependencies:** only the URL shortener, student API and QR generator need packages (Flask, FastAPI, qrcode); the rest use the standard library.
- **Documented:** each project explains usage, how to run its tests, and its known limitations.

## Repository layout

```text
my-project/
├── .github/                   # CI workflow, Dependabot, issue and PR templates
├── url-shortener/
├── markdown-converter/
├── log-analyzer/
├── password-toolkit/
├── task-tracker-cli/
├── expense-tracker/
├── text-analyzer/
├── file-organizer/
├── student-management/
├── qr-generator/
├── portfolio-website/
├── profile-readme/            # source for the GitHub profile page
├── CONTRIBUTING.md · SECURITY.md · CHANGELOG.md
└── Makefile · ruff.toml · .editorconfig
```

## Quick start

```bash
git clone https://github.com/Denwin437/my-project.git
cd my-project/url-shortener
pip install -r requirements.txt
pytest
python app.py
```

<details>
<summary><b>Try the other tools</b></summary>

```bash
python password-toolkit/passwords.py generate -l 20
python log-analyzer/loganalyzer.py log-analyzer/sample.log
python task-tracker-cli/tasks.py add "Write tests" -p high
python expense-tracker/expenses.py add 12.50 food
echo "# Hello **world**" | python markdown-converter/md2html.py
echo "Short sentences read fast." | python text-analyzer/analyzer.py
```

</details>

## Tech stack

Python, Flask, FastAPI, SQLite, pytest, ruff, GitHub Actions, CodeQL, HTML and CSS.

## Roadmap

- [ ] Add authentication and rate limiting to the URL shortener
- [ ] Support nested lists and tables in the Markdown converter
- [ ] Package the CLI tools for `pip install`
- [ ] Add a Dockerfile for the API

## Contributing and security

See [CONTRIBUTING.md](CONTRIBUTING.md) to get started and [SECURITY.md](SECURITY.md) to report a vulnerability.

## License

MIT, see [LICENSE](LICENSE).

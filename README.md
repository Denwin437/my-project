<p align="center">
  <img src="https://capsule-render.vercel.app/api?type=waving&color=0:0f172a,100:38bdf8&height=160&section=header&text=Python%20Projects%20Portfolio&fontSize=38&fontColor=ffffff&fontAlignY=40&desc=Small%2C%20tested%2C%20production-style%20tools&descSize=16&descAlignY=62" alt="Python Projects Portfolio" />
</p>

<p align="center">
  <img src="https://github.com/Denwin437/my-project/actions/workflows/ci.yml/badge.svg" alt="CI" />
  <img src="https://img.shields.io/badge/python-3.10%2B-3776AB?logo=python&logoColor=white" alt="Python 3.10+" />
  <img src="https://img.shields.io/badge/tests-47%20passing-22c55e" alt="47 tests" />
  <img src="https://img.shields.io/badge/license-MIT-blue" alt="MIT license" />
</p>

Eight self-contained projects, each with its own README, unit tests and automated CI. They cover command-line tools, a REST API, text and log processing, and security-minded input handling.

## Projects

| Project | What it does | Stack | Tests |
|---------|--------------|-------|:-----:|
| [**url-shortener**](url-shortener) | REST API that shortens URLs, redirects and counts clicks | Flask · SQLite | 5 |
| [**markdown-converter**](markdown-converter) | Markdown → HTML converter written from scratch, safe against HTML injection | Python | 10 |
| [**log-analyzer**](log-analyzer) | Summarizes web server logs: status codes, error rate, top IPs and paths | Python | 6 |
| [**password-toolkit**](password-toolkit) | Secure password and passphrase generator with a strength checker | Python · `secrets` | 8 |
| [**task-tracker-cli**](task-tracker-cli) | Command-line to-do manager with priorities | Python | 6 |
| [**expense-tracker**](expense-tracker) | Logs spending to CSV and summarizes by category or month | Python | 5 |
| [**text-analyzer**](text-analyzer) | Word statistics, reading time and a readability score | Python | 7 |
| [**portfolio-website**](portfolio-website) | Responsive dark-theme personal site | HTML · CSS | n/a |

## Engineering practices

- **Tested:** 47 unit tests, including CLI end-to-end tests and API tests with Flask's test client.
- **Continuous integration:** GitHub Actions runs every project's tests on each push and pull request.
- **Secure by default:** cryptographically secure randomness (`secrets`), HTML escaping and URL-scheme filtering, and parameterized SQL queries.
- **Input validation:** every CLI and API rejects bad input with clear errors instead of crashing.
- **Minimal dependencies:** only the URL shortener needs a package (Flask); the rest use the standard library.
- **Documented:** each project explains usage, how to run its tests, and its known limitations.

## Repository layout

```text
my-project/
├── .github/workflows/ci.yml   # runs each project's tests
├── url-shortener/
├── markdown-converter/
├── log-analyzer/
├── password-toolkit/
├── task-tracker-cli/
├── expense-tracker/
├── text-analyzer/
├── portfolio-website/
└── profile-readme/            # source for the GitHub profile page
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

<p>
  <img src="https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/Flask-000000?style=flat-square&logo=flask&logoColor=white" alt="Flask" />
  <img src="https://img.shields.io/badge/SQLite-003B57?style=flat-square&logo=sqlite&logoColor=white" alt="SQLite" />
  <img src="https://img.shields.io/badge/pytest-0A9EDC?style=flat-square&logo=pytest&logoColor=white" alt="pytest" />
  <img src="https://img.shields.io/badge/GitHub%20Actions-2088FF?style=flat-square&logo=githubactions&logoColor=white" alt="GitHub Actions" />
  <img src="https://img.shields.io/badge/HTML5-E34F26?style=flat-square&logo=html5&logoColor=white" alt="HTML5" />
  <img src="https://img.shields.io/badge/CSS3-1572B6?style=flat-square&logo=css3&logoColor=white" alt="CSS3" />
</p>

## Roadmap

- [ ] Add authentication and rate limiting to the URL shortener
- [ ] Support nested lists and tables in the Markdown converter
- [ ] Package the CLI tools for `pip install`
- [ ] Add a Dockerfile for the API

## License

MIT, see [LICENSE](LICENSE).

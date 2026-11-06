# Contributing

Thanks for your interest. Bug reports, fixes and ideas are welcome.

## Set up
```bash
git clone https://github.com/Denwin437/my-project.git
cd my-project
pip install pytest ruff
pip install -r url-shortener/requirements.txt   # only needed for the URL shortener
```

## Before opening a pull request
1. Create a branch from `main`.
2. Make a focused change and add or update tests.
3. Run the checks:
   ```bash
   ruff check .
   make test
   ```
4. Open a pull request and fill in the template.

## Style
- Follow the existing code style and keep functions small and testable.
- Validate input and raise clear errors.
- Use [Conventional Commit](https://www.conventionalcommits.org) style messages, for example `fix: handle empty log files`.

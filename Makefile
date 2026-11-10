PROJECTS := task-tracker-cli expense-tracker url-shortener text-analyzer password-toolkit markdown-converter log-analyzer file-organizer

.PHONY: test lint all

all: lint test

lint:
	ruff check .

test:
	@for p in $(PROJECTS); do \
		echo "== $$p"; \
		(cd $$p && python -m pytest -q -p no:cacheprovider) || exit 1; \
	done
